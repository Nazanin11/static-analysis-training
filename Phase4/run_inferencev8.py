#!/usr/bin/env python3
"""
run_inference.py — v8.0

Summary of key behavior:
- Uses Qwen3-Coder-Next via llama.cpp with full-source + RAG + semantic profile prompt.
- Free reasoning (no GBNF); model emits JSON inside a fenced ```json``` block.
- Triple-voting: each finding is evaluated 3 times with slightly perturbed prompts.
  The final verdict is chosen by majority vote; all votes are logged.
- Deterministic overrides kept only for architecture invariants
  (alloca-in-loop semantic confirmation, canonical packet-walker patterns,
   missing-header-guard demotion, malloc-sized strcpy). FIXME overrides removed.
- Hallucination heuristic is conservative and no longer misfires on "thread-safe".
- FIXME verdicts are fully owned by the model.
- Type-confusion rule includes an ASSERT-only SMELL directive for internal FIB types.
"""

import json
import os
import re
import time
import gc
from collections import Counter
from llama_cpp import Llama

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL_PATH  = "/home/master/models/qwen3-coder-next-q6/Qwen3-Coder-Next-Q6_K-00001-of-00003.gguf"
INPUT_JSON  = "llm_triage_batches.json"
OUTPUT_JSON = "llm_triage_results_Pilot.json"
#INPUT_JSON  = "latest_batches.json"
#OUTPUT_JSON = "latest_result.json"


# Triple-voting configuration
NUM_VOTES   = 3

# ---------------------------------------------------------------------------
# System prompt — free reasoning + fenced JSON + refined cpp/type-confusion
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are a Lead C/Network Security Auditor specialising in routing-daemon code (BGP, OSPF, BFD, Babel).
You will receive the full source file first (background), then RAG context (struct/function/macro
definitions and call-graph edges), then a semantic feature profile, and finally the FINDING with
the local code snippet around the flagged line.

## Triage taxonomy
VULN — Exploitable flaw reachable from untrusted network input, or a concurrency hazard that can
cause memory corruption / DoS.
SMELL — Code quality / technical-debt issue with no direct exploitability.
FP — A safe C idiom that the scanner misclassified.

## Chain-of-thought (MANDATORY — write ALL steps before emitting JSON)
1. Locate the exact flagged line in the LOCAL SNIPPET at the bottom of the prompt. Quote it verbatim.
2. 2. Identify the enclosing function and its callers. If CG CALLERS is empty AND is_inline_func is true AND no GREP CALLERS block is present, set confidence ≤ 6 and verdict = SMELL. Do NOT invent call chains.
3. Determine whether untrusted network data reaches this line. Cite the actual call chain.
4. Apply the rule-specific playbook below. State which playbook branch applies and why.
5. State your verdict and why, referencing specific source lines as evidence.
6. ONLY THEN emit the JSON block (see format below).

## Rule-specific playbooks

- cpp/alloca-in-loop:
  VULN if alloca() is inside a loop AND the loop bound is controlled by network input
  (e.g. packet field, NLRI count, flen from wire). Stack frame never shrinks mid-loop.
  SMELL if the loop is bounded by a compile-time constant or internal routing-table size.
  FP if alloca() is outside any loop.

- cpp/type-confusion:
  FP if the cast is immediately preceded by a switch/if on a type-tag field.
  FP if the function name clearly indicates it fills/initialises a specific net type
  (e.g. net_fill_ip4, net_fill_vpn6, NET_ADDR_VPN4 macro constructors).
  FP if the cast occurs inside a MACRO, but the macro's invocation site in the caller
  function is strictly guarded by a switch(addr_type) or if(type == X) check — the
  guard does not need to be inside the macro itself, only present at the call site.
  SMELL if the only missing guard is an ASSERT() or ASSERT_DIE() that compiles out in
  release builds, BUT the table/struct type is set at initialization and never externally
  mutable at runtime. VULN requires the type mismatch to be directly injectable from
  unvalidated network input without a prior memory corruption primitive.
  VULN if the cast happens without ANY type guard (neither in the macro nor at the call
  site) AND the pointer originates from network input.
  SMELL otherwise.

- cpp/unused-static-function:
  FP if the function appears inside an EXPENSIVE_CHECK(), ASSUME(), or similar debug macro
  (check the RAG context for the macro body).
  SMELL if genuinely unreferenced after checking macros.

- fixme-comment / cpp/fixme-comment:
  Read the FULL comment text visible in the LOCAL SNIPPET.
  VULN if the comment text conveys a safety/concurrency hazard, including but not limited to:
    thread-unsafe, non-atomic, race condition, data race, deadlock, buffer overflow,
    stack overflow, injection, UAF, use-after-free, freed, concurrent, race.
  Use semantic judgment — a comment saying "protocols may still use the freed address"
  is a UAF/race hazard even if it does not use the exact words "use-after-free".
  SMELL for ALL other FIXME/TODO comments regardless of content.
  Do NOT classify FIXME as VULN based on words like "undefined", "hack", "should",
  "better", "allow", "support", "missing", "incomplete".

- cpp/suspicious-pointer-scaling / cpp/suspicious-pointer-scaling-void:
  FP for canonical BIRD/OSPF/BGP zero-copy packet-walking:
  ((void*)pkt)+offset, ((void*)pkt)+hlen, ((void*)hdr)+sizeof(*hdr), (auth+1), (pkt+1).
  FP if enclosing function contains: build_, encode_, decode_, rx_, tx_, parse_,
  ospf_rx_, bgp_read_, send_, recv_, ospf_lsupd_, ospf_auth_.
  VULN only if pointer arithmetic crosses struct-type boundaries AND pointer is from
  unvalidated network read without a length check.
  SMELL if uncertain — do not guess VULN without concrete evidence.

- missing-header-guard / cpp/missing-header-guard:
  SMELL always. Not exploitable.

- cpp/unbounded-write (strcpy/strcat):
  FP if the destination buffer was allocated with malloc/alloca whose size argument
  is the sum of the source string lengths (malloc(len) where len = sum of strlen(src)+1).
  VULN only if the destination is a fixed-size stack buffer and the source is
  network-controlled input without a length check.

- cpp/path-injection / cpp/include-non-header:
  Trace whether the path originates from argv/config (user-controlled) vs compile-time constant.
  VULN only if user-controlled and unvalidated from an attacker-controlled context
  (e.g. remote management protocol). Local CLI-only paths are SMELL unless explicitly
  documented as a security boundary.

## Directives
- INSUFFICIENT CONTEXT: If the LOCAL SNIPPET does NOT show the flagged line, write
  "INSUFFICIENT CONTEXT" in mechanical_evidence and cap confidence at 5.
- Never invent function names, line numbers, or execution paths not visible in the provided source.
- Quote actual source lines as evidence — do not paraphrase.
- verdict MUST be exactly one of: VULN, SMELL, FP.

## Output format
After your reasoning, emit EXACTLY this fenced block and nothing after it:

```json
{
  "pattern_name": "<rule id>",
  "mechanical_evidence": "<quoted source lines proving your verdict>",
  "rationale": "<one paragraph tying evidence to verdict>",
  "verdict": "<VULN|SMELL|FP>",
  "confidence": <1-10>
}
```
"""

# ---------------------------------------------------------------------------
# Compiled regexes & helpers
# ---------------------------------------------------------------------------
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Used only for lightweight hallucination checks (never overrides verdict)
_FIXME_HAZARD_RE = re.compile(
    r"\bthread[- ](unsafe|safe)\b"       # compound only — bare "thread" excluded
    r"|\bnon[- ]atomic\b"
    r"|\bdata\s+race\b"
    r"|\brace\s+condition\b"
    r"|\bUAF\b|use[- ]after[- ]free"
    r"|\bbuffer\s+overflow\b"
    r"|\bstack\s+overflow\b"
    r"|\binjection\b"
    r"|\bdeadlock\b",
    re.IGNORECASE,
)

_PACKET_WALKER_FUNC_RE = re.compile(
    r"\b(build_|encode_|decode_|ospf_rx|ospf_lsupd|ospf_auth|bgp_read_|"
    r"send_|recv_|parse_|rx_|tx_)",
    re.IGNORECASE,
)
_PACKET_WALKER_PATTERN_RE = re.compile(r"\(\s*\(\s*void\s*\*\s*\)", re.IGNORECASE)
_MALLOC_LEN_RE = re.compile(r"\bmalloc\s*\([^)]*\blen\b", re.IGNORECASE)

# For hallucination detection
_C_IDENTIFIER_RE = re.compile(r"\b([a-z_][a-z0-9_]{3,})\s*\(", re.IGNORECASE)


def sanitize_source(text: str) -> str:
    return _CONTROL_CHAR_RE.sub("", text)

# ---------------------------------------------------------------------------
# JSON extraction from CoT text
# ---------------------------------------------------------------------------

def extract_json_from_text(text: str) -> dict:
    """Extract the last JSON object from free-form reasoning text.

    Strategy:
      1. Last ```json { ... } ``` fenced block.
      2. Last bare { ... } block.
      3. Regex-based key-by-key reconstruction.
    """
    fenced = re.findall(r"```json\s*(\{[\s\S]*?\})\s*```", text)
    if fenced:
        try:
            return json.loads(fenced[-1])
        except json.JSONDecodeError:
            pass

    brace_blocks = re.findall(r"(\{[^{}]{20,}\})", text, re.DOTALL)
    if brace_blocks:
        for block in reversed(brace_blocks):
            try:
                return json.loads(block)
            except json.JSONDecodeError:
                continue

    result = {}
    for key in ("pattern_name", "mechanical_evidence", "rationale", "verdict"):
        m = re.search(rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
        if m:
            result[key] = m.group(1)
    conf_m = re.search(r'"confidence"\s*:\s*(\d+)', text)
    if conf_m:
        result["confidence"] = int(conf_m.group(1))

    required = {"pattern_name", "mechanical_evidence", "rationale", "verdict", "confidence"}
    if required.issubset(result.keys()):
        return result

    raise ValueError(f"No valid JSON found in model output. Last 300 chars: {text[-300:]}")

# ---------------------------------------------------------------------------
# Hallucination heuristics (never override, only flag)
# ---------------------------------------------------------------------------

def check_hallucination(result: dict, batch: dict, finding: dict) -> list[str]:
    flags: list[str] = []
    source    = batch.get("source_code", "")
    mech      = result.get("mechanical_evidence", "")
    rationale = result.get("rationale", "")
    verdict   = result.get("verdict", "")

    src_lines = source.splitlines()
    line_refs = re.findall(r"\bline[s]?\s+(\d+)\b", mech + " " + rationale, re.IGNORECASE)
    for lr in line_refs:
        actual_lines = batch.get("actual_line_count") or len(src_lines)
        if int(lr) > len(src_lines) + 5:
            flags.append(f"Invented line number {lr} (file has {len(src_lines)} lines)")

    mentioned_funcs = set(_C_IDENTIFIER_RE.findall(mech))
    stdlib = {"malloc", "free", "strcpy", "strlen", "memcpy", "alloca",
              "printf", "snprintf", "sprintf", "fprintf", "assert"}
    for fn in mentioned_funcs:
        if fn.lower() in stdlib:
            continue
        if fn not in source:
            flags.append(f"Function '{fn}' in evidence not found in source")

    # Conservative: no longer key on bare "safe" to avoid thread-safe misfires.
    safe_kw = re.compile(r"\b(no overflow|bounded|length.check|validated)\b", re.I)
    vuln_kw = re.compile(r"\b(overflow|unbounded|inject|corrupt|UAF|race|deadlock)\b", re.I)

    if verdict == "VULN" and safe_kw.search(mech) and not vuln_kw.search(mech):
        flags.append("VULN verdict but evidence contains only safe-language keywords")
    if verdict == "FP" and vuln_kw.search(mech) and not safe_kw.search(mech):
        flags.append("FP verdict but evidence contains only vulnerability-language keywords")

    return flags

# ---------------------------------------------------------------------------
# Deterministic overrides — architecture invariants only
# ---------------------------------------------------------------------------

def apply_deterministic_overrides(
    rule_id: str, sem: dict, llm_verdict: str,
    mech_evidence: str, batch: dict, finding: dict,
) -> tuple[str | None, str | None]:
    """Return (new_verdict, reason) or (None, None) if no override.

    Only used for invariants that are strictly more reliable than the model:
      - alloca-in-loop semantic confirmation
      - missing-header-guard demotion
      - canonical packet-walker patterns
      - malloc-sized strcpy FP.
    """

    # alloca-in-loop: semantic profile knows if we're really inside a loop
    if rule_id == "cpp/alloca-in-loop":
        if sem.get("contains_alloca") and sem.get("inside_loop"):
            if llm_verdict != "VULN":
                return (
                    "VULN",
                    "OVERRIDE: alloca() confirmed inside loop by semantic profile. "
                    "Stack grows unboundedly per iteration — network-controlled loop = DoS.",
                )

    # fixme-comment: overrides removed — model owns verdicts

    # type-confusion: only demote VULN when guarded by switch tag in semantics
    if rule_id == "cpp/type-confusion":
        if sem.get("guarded_by_switch_tag") and llm_verdict == "VULN":
            return "FP", "OVERRIDE: Cast is guarded by a type-discriminant switch in caller."

    # missing-header-guard always SMELL
    if rule_id in ("missing-header-guard", "cpp/missing-header-guard"):
        if llm_verdict == "VULN":
            return "SMELL", "OVERRIDE: Missing header guard is not exploitable."

    # suspicious-pointer-scaling: canonical packet-walker idioms
    if rule_id in ("cpp/suspicious-pointer-scaling-void", "cpp/suspicious-pointer-scaling"):
        ctx        = finding.get("RAG_Context", "")
        local_snip = finding.get("local_snippet", "")
        is_packet_func    = (bool(_PACKET_WALKER_FUNC_RE.search(ctx)) or
                             bool(_PACKET_WALKER_FUNC_RE.search(local_snip)))
        is_walker_pattern = bool(_PACKET_WALKER_PATTERN_RE.search(mech_evidence))
        if is_packet_func and is_walker_pattern and llm_verdict == "VULN":
            return (
                "FP",
                "OVERRIDE: Matches canonical BIRD zero-copy packet-walker idiom "
                "((void*)pkt + offset) inside a packet-processing function.",
            )

    # unbounded-write: malloc-sized strcpy pattern
    if rule_id in ("cpp/unbounded-write", "c:S5042"):
        src_window = finding.get("local_snippet", "")
        if bool(_MALLOC_LEN_RE.search(src_window)) and llm_verdict == "VULN":
            return (
                "FP",
                "OVERRIDE: strcpy destination is malloc'd to the exact sum of "
                "source string lengths — buffer is correctly sized, not exploitable.",
            )
    if sem.get("is_test_file") and llm_verdict == "VULN":
        return (
            "SMELL",
            "OVERRIDE: Finding is in a test file — not a production code path.",
        )

    return None, None

# ---------------------------------------------------------------------------
# Prompt builder — SOURCE first, FINDING + LOCAL SNIPPET last
# ---------------------------------------------------------------------------

def build_prompt(batch: dict, finding: dict, vote_id: int | None = None) -> str:
    sem_str    = json.dumps(finding.get("Semantic_Profile", {}), indent=2)
    rag_str    = finding.get("RAG_Context", "No external context available.")
    source     = sanitize_source(batch.get("source_code", ""))
    local_snip = finding.get("local_snippet", "")
    vote_tag   = f"[VOTE_ID: {vote_id}]" if vote_id is not None else ""

    grep_block = ""
    if "GREP CALLERS" in rag_str:
        idx = rag_str.index("--- [GREP CALLERS")
        grep_block = "\n## CALLER CONTEXT (grep call sites — check for null guards)\n" + rag_str[idx:]

    return f"""\
## FULL SOURCE CODE OF '{batch['file']}' (background — read for full context) {vote_tag}
{source}

## RAG CONTEXT (struct/function/macro definitions + call-graph)
{rag_str}

## SEMANTIC FEATURE PROFILE
{sem_str}

## STATIC ANALYSIS FINDING  ← FOCUS HERE
File     : {batch['file']}
Line     : {finding['Line']}
Rule ID  : {finding['Rule_ID']}
Severity : {finding.get('Severity', 'unknown')}
Tool     : {finding.get('Tool', 'unknown')}
Message  : {finding['Message']}

## LOCAL SNIPPET (±20 lines around flagged line — this is your primary evidence)
{local_snip}
{grep_block}
"""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    pipeline_start = time.time()

    if not os.path.exists(INPUT_JSON):
        print(f"[ERROR] {INPUT_JSON} not found. Run build_batches.py first.")
        return

    results: list[dict] = []
    processed_ids: set[int] = set()

    if os.path.exists(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, "r") as fh:
                raw = json.load(fh)
            for r in raw:
                if any(v.get("verdict") == "UNKNOWN" for v in r.get("verdict_array", [])):
                    print(f"[RETRY] Batch {r.get('batch_id')} had UNKNOWN — re-queuing.")
                    continue
                results.append(r)
                processed_ids.add(r["batch_id"])
            print(f"[CACHE] Resumed with {len(processed_ids)} already-processed batches.")
        except Exception as e:
            print(f"[WARN] Cache load failed ({e}), starting fresh.")

    with open(INPUT_JSON, "r") as fh:
        batches: list[dict] = json.load(fh)

    pending = [b for b in batches if b["batch_id"] not in processed_ids]
    print(f"[INFO] {len(pending)} batches to process.")

    print("-> Initialising Qwen3-Coder-Next on GPU ...")
    llm = Llama(
        model_path   = MODEL_PATH,
        n_gpu_layers = -1,
        n_ctx        = 98304,
        n_batch      = 8192,
        use_mlock    = True,
        flash_attn   = True,
        verbose      = False,
    )

    for i, batch in enumerate(pending):
        bid       = batch["batch_id"]
        file_name = batch["file"]
        n_total   = len(pending)

        print(f"\n[{i+1}/{n_total}] Batch {bid} — {file_name}")
        file_t0 = time.time()

        batch_result = {
            "batch_id":      bid,
            "file":          file_name,
            "findings":      [],
            "verdict_array": [],
        }

        for f_idx, finding in enumerate(batch["findings"]):
            rule = finding.get("Rule_ID", "?")
            line = finding.get("Line", "?")
            print(f"  -> [{f_idx+1}] Line {line} ({rule}) ... ", end="", flush=True)
            t0 = time.time()

            est_tokens = (len(SYSTEM_PROMPT) + len(json.dumps(finding)) + len(batch.get("source_code", ""))) // 4
            print(f"~{est_tokens:,} tok * {NUM_VOTES} votes ... ", end="", flush=True)

            try:
                vote_results: list[dict] = []

                for vote_id in range(1, NUM_VOTES + 1):
                    prompt = build_prompt(batch, finding, vote_id=vote_id)
                    response = llm.create_chat_completion(
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user",   "content": prompt},
                        ],
                        temperature    = 0.0,
                        repeat_penalty = 1.05,
                        max_tokens     = 12288,
                    )

                    raw_text = response["choices"][0]["message"]["content"]
                    partial = extract_json_from_text(raw_text)

                    try:
                        partial["confidence"] = max(1, min(10, int(partial.get("confidence", 1))))
                    except (ValueError, TypeError):
                        partial["confidence"] = 1

                    partial["pattern_name"] = rule
                    partial["full_reasoning"] = raw_text
                    vote_results.append(partial)

                # Triple-voting aggregation
                verdict_counts = Counter(v["verdict"] for v in vote_results)
                # Require majority (>=2) for VULN; otherwise prefer consensus if any
                final_verdict = None
                if verdict_counts.get("VULN", 0) >= 2:
                    final_verdict = "VULN"
                else:
                    # pick any label with count >=2
                    for label, cnt in verdict_counts.items():
                        if cnt >= 2:
                            final_verdict = label
                            break
                if final_verdict is None:
                    # 1-1-1 split: treat as SMELL and mark for review
                    final_verdict = "SMELL"

                # Choose representative vote for the final verdict (first matching)
                rep = next(v for v in vote_results if v["verdict"] == final_verdict)
                result = dict(rep)  # shallow copy

                # Attach all vote details for audit
                result["vote_details"] = [
                    {
                        "verdict": v.get("verdict"),
                        "confidence": v.get("confidence"),
                        "mechanical_evidence": v.get("mechanical_evidence", ""),
                    }
                    for v in vote_results
                ]

                mech   = result.get("mechanical_evidence", "").strip()
                result["human_review_required"] = False

                if result["confidence"] <= 5 or "INSUFFICIENT CONTEXT" in mech.upper():
                    result["human_review_required"] = True

                if len(mech) < 15 or mech.lower() in {"none", "n/a", "null", "empty", ""}:
                    result["human_review_required"] = True
                    result["rationale"] = (
                        "[SYSTEM WARNING: Evidence too weak — human review required.]\n"
                        + result.get("rationale", "")
                    )

                # Hallucination heuristics
                hallucination_flags = check_hallucination(result, batch, finding)
                result["hallucination_suspect"] = len(hallucination_flags) > 0
                result["hallucination_flags"]   = hallucination_flags
                if hallucination_flags:
                    result["human_review_required"] = True
                    print(f"\n  [HALLUCINATION?] {hallucination_flags}", end="")

                # Deterministic overrides (architecture invariants)
                sem = finding.get("Semantic_Profile", {})
                override_verdict, override_reason = apply_deterministic_overrides(
                    rule, sem, result["verdict"], mech, batch, finding
                )

                if override_verdict is not None:
                    result["verdict"]               = override_verdict
                    result["human_review_required"] = True
                    result.setdefault("override_chain", []).append(override_reason)
                    result["rationale"] = (
                        f"{override_reason}\n\n"
                        f"--- Original LLM Rationale (winning vote) ---\n"
                        f"{result.get('rationale', '')}"
                    )

                result["finding_index"] = f_idx

            except Exception as exc:
                print(f"\n  [ERROR] {exc}")
                result = {
                    "finding_index":        f_idx,
                    "pattern_name":         rule,
                    "mechanical_evidence":  f"Inference failure: {exc}",
                    "rationale":            str(exc),
                    "verdict":              "UNKNOWN",
                    "confidence":           1,
                    "human_review_required":True,
                    "full_reasoning":       "",
                    "hallucination_suspect":False,
                    "hallucination_flags":  [],
                    "vote_details":         [],
                }

            elapsed = time.time() - t0
            flag    = "[REVIEW]"  if result.get("human_review_required") else ""
            hflag   = "[HALLUC?]" if result.get("hallucination_suspect") else ""
            print(f"Verdict: {result['verdict']} {flag}{hflag} ({elapsed:.1f}s)")
            batch_result["verdict_array"].append(result)

        results.append(batch_result)

        with open(OUTPUT_JSON, "w") as fh:
            json.dump(results, fh, indent=4)
        gc.collect()

        print(f"  [Batch done in {time.time() - file_t0:.1f}s]")

    total_min = (time.time() - pipeline_start) / 60
    print("\n" + "=" * 60)
    print(f"Pipeline complete. {len(results)} batches processed.")
    print(f"Total time: {total_min:.1f} minutes")
    print(f"Output: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()

