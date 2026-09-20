import json
import csv
from collections import Counter, defaultdict

# ============================================================
# INPUT / OUTPUT
# ============================================================

RESULTS_JSON = "llm_triage_results_Pilot_Qwen3.6.json"

# Optional: final batch input file
BATCHES_JSON = "/home/nazanin/Projects/bird-2.17.1/reports/llm_triage/llm_triage_batches_with_cwe.json"

LOW_CONFIDENCE_THRESHOLD = 6

OUTPUT_CSV = "qwen36_analysis_low_confidence.csv"

# Batch 1-5 belong to the previous batch configuration
IGNORE_BATCHES = set(range(1, 6))


# ============================================================
# LOAD RESULTS
# ============================================================

with open(RESULTS_JSON, "r", encoding="utf-8") as f:
    results_all = json.load(f)


# Ignore old batches 1-5
results = [
    r for r in results_all
    if r.get("batch_id") not in IGNORE_BATCHES
]


# ============================================================
# OPTIONAL: LOAD BATCH INPUT
# ============================================================

batch_metadata = {}

try:
    with open(BATCHES_JSON, "r", encoding="utf-8") as f:
        batch_data = json.load(f)

    for batch in batch_data:
        batch_metadata[batch.get("batch_id")] = batch

    batch_input_loaded = True

except FileNotFoundError:
    batch_input_loaded = False


# ============================================================
# HELPERS
# ============================================================

def get_main_vote(result):
    """
    The main verdict/confidence stored in the result's
    verdict_array.

    In the actual output structure, verdict_array contains
    the model result and vote_details contains the 3 votes.
    """

    verdict_array = result.get("verdict_array", [])

    if not verdict_array:
        return None

    return verdict_array[0]


def get_verdict(result):
    vote = get_main_vote(result)

    if not vote:
        return "UNKNOWN"

    return vote.get("verdict", "UNKNOWN")


def get_confidence(result):
    vote = get_main_vote(result)

    if not vote:
        return None

    confidence = vote.get("confidence")

    if isinstance(confidence, (int, float)):
        return float(confidence)

    return None


def get_rule(result):
    vote = get_main_vote(result)

    if not vote:
        return "UNKNOWN"

    return vote.get("pattern_name", "UNKNOWN")


def get_tool(rule):
    rule = str(rule)

    if "CodeQL" in rule:
        return "CodeQL"

    if "Semgrep" in rule:
        return "Semgrep"

    if "Cppcheck" in rule:
        return "Cppcheck"

    # SonarQube rules in this project use c:Sxxxx
    if rule.startswith("c:"):
        return "SonarQube"

    return "Other"


def get_vote_details(result):
    vote = get_main_vote(result)

    if not vote:
        return []

    return vote.get("vote_details", [])


def get_vote_verdicts(result):
    votes = get_vote_details(result)

    return [
        v.get("verdict")
        for v in votes
        if v.get("verdict")
    ]

def get_human_review_required(result):
    vote = get_main_vote(result)

    if not vote:
        return None

    return vote.get("human_review_required")


def get_hallucination_suspect(result):
    vote = get_main_vote(result)

    if not vote:
        return None

    return vote.get("hallucination_suspect")


def get_hallucination_flags(result):
    vote = get_main_vote(result)

    if not vote:
        return []

    flags = vote.get("hallucination_flags", [])

    return flags if isinstance(flags, list) else []
def get_severity(result):
    """
    Severity is not stored in the Qwen3.6 result itself.
    Try to recover it from the final batch input using batch_id.
    """

    batch_id = result.get("batch_id")

    if batch_id not in batch_metadata:
        return "UNKNOWN"

    batch = batch_metadata[batch_id]

    # Different possible structures are handled safely.
    findings = batch.get("findings", [])

    if findings:
        finding = findings[0]

        return (
            finding.get("Severity")
            or finding.get("severity")
            or "UNKNOWN"
        )

    return "UNKNOWN"


# ============================================================
# BASIC DATA COLLECTION
# ============================================================

total = len(results)

verdict_counts = Counter()
confidences = []

tool_data = defaultdict(list)
severity_data = defaultdict(list)
rule_data = defaultdict(list)

low_confidence = []
unknown_results = []

consistent = 0
inconsistent = 0
human_review_counts = Counter()
hallucination_suspect_counts = Counter()
hallucination_flag_counts = Counter()

findings_with_hallucination_flags = 0
total_hallucination_flags = 0

for result in results:

    verdict = get_verdict(result)
    confidence = get_confidence(result)
    rule = get_rule(result)
    tool = get_tool(rule)
    severity = get_severity(result)
    # --------------------------------------------------------
    # RELIABILITY / HALLUCINATION METADATA
    # --------------------------------------------------------

    human_review = get_human_review_required(result)
    hallucination_suspect = get_hallucination_suspect(result)
    hallucination_flags = get_hallucination_flags(result)

    human_review_counts[human_review] += 1
    hallucination_suspect_counts[hallucination_suspect] += 1

    if hallucination_flags:
        findings_with_hallucination_flags += 1
        total_hallucination_flags += len(hallucination_flags)

        hallucination_flag_counts.update(
            hallucination_flags
        )

    verdict_counts[verdict] += 1

    if confidence is not None:
        confidences.append(confidence)

    tool_data[tool].append(result)
    severity_data[severity].append(result)
    rule_data[rule].append(result)

    if confidence is not None and confidence <= LOW_CONFIDENCE_THRESHOLD:
        low_confidence.append(result)

    if verdict == "UNKNOWN":
        unknown_results.append(result)

    # --------------------------------------------------------
    # 3-VOTE CONSISTENCY
    # --------------------------------------------------------

    votes = get_vote_verdicts(result)

    if len(votes) == 3 and len(set(votes)) == 1:
        consistent += 1
    else:
        inconsistent += 1


# ============================================================
# HEADER
# ============================================================

print("=" * 72)
print("QWEN3.6 — FULL ANALYSIS")
print("=" * 72)

print(f"Input results      : {RESULTS_JSON}")

if batch_input_loaded:
    print(f"Batch input        : {BATCHES_JSON}")
else:
    print("Batch input        : NOT FOUND")

print("Ignored batches    : 1-5")
print("Analyzed batches   : 6-226")
print(f"Analyzed findings  : {total}")

print()


# ============================================================
# VERDICT DISTRIBUTION
# ============================================================

print("=" * 72)
print("VERDICT DISTRIBUTION")
print("=" * 72)

for verdict in ["VULN", "SMELL", "FP", "UNKNOWN"]:

    count = verdict_counts.get(verdict, 0)

    pct = (
        count / total * 100
        if total
        else 0
    )

    print(
        f"{verdict:<8}: "
        f"{count:4d} "
        f"({pct:5.1f}%)"
    )

print()


# ============================================================
# CONFIDENCE
# ============================================================

print("=" * 72)
print("CONFIDENCE")
print("Confidence scale: 1-10")
print("=" * 72)

if confidences:

    avg_conf = sum(confidences) / len(confidences)

    print(
        f"Average : {avg_conf:.3f}/10"
    )

    print(
        f"Minimum : {min(confidences):.1f}/10"
    )

    print(
        f"Maximum : {max(confidences):.1f}/10"
    )

    print()
    print("Confidence distribution:")

    ranges = [
        ("1-3", lambda x: 1 <= x <= 3),
        ("4-6", lambda x: 4 <= x <= 6),
        ("7-8", lambda x: 7 <= x <= 8),
        ("9-10", lambda x: 9 <= x <= 10),
    ]

    for label, condition in ranges:

        count = sum(
            condition(x)
            for x in confidences
        )

        pct = count / len(confidences) * 100

        print(
            f"{label:<6}: "
            f"{count:4d} "
            f"({pct:5.1f}%)"
        )

print()


# ============================================================
# CONFIDENCE BY VERDICT
# ============================================================

print("=" * 72)
print("CONFIDENCE BY VERDICT")
print("=" * 72)

for verdict in ["VULN", "SMELL", "FP", "UNKNOWN"]:

    values = [
        get_confidence(r)
        for r in results
        if get_verdict(r) == verdict
        and get_confidence(r) is not None
    ]

    if values:

        print(
            f"{verdict:<8}: "
            f"{len(values):4d} findings | "
            f"average confidence = "
            f"{sum(values)/len(values):.3f}/10"
        )

print()


# ============================================================
# 3-VOTE CONSISTENCY
# ============================================================

print("=" * 72)
print("3-VOTE CONSISTENCY")
print("=" * 72)

consistency_pct = (
    consistent / total * 100
    if total
    else 0
)

print(f"Findings     : {total}")
print(f"Consistent   : {consistent}")
print(f"Inconsistent : {inconsistent}")
print(f"Consistency  : {consistency_pct:.1f}%")

print()


# ============================================================
# VOTE PATTERNS
# ============================================================

print("=" * 72)
print("3-VOTE PATTERNS")
print("=" * 72)

vote_patterns = Counter()

for result in results:

    votes = get_vote_verdicts(result)

    if votes:

        pattern = " / ".join(votes)

        vote_patterns[pattern] += 1

for pattern, count in vote_patterns.most_common():

    print(
        f"{count:4d}  {pattern}"
    )

print()


# ============================================================
# VERDICT DISTRIBUTION BY TOOL
# ============================================================

print("=" * 72)
print("VERDICT DISTRIBUTION BY TOOL")
print("=" * 72)

for tool in [
    "SonarQube",
    "CodeQL",
    "Cppcheck",
    "Semgrep",
    "Other"
]:

    items = tool_data.get(tool, [])

    if not items:
        continue

    counts = Counter(
        get_verdict(r)
        for r in items
    )

    print()
    print(tool)
    print("-" * 40)
    print(f"Total: {len(items)}")

    for verdict in [
        "VULN",
        "SMELL",
        "FP",
        "UNKNOWN"
    ]:

        count = counts.get(verdict, 0)

        pct = (
            count / len(items) * 100
            if items
            else 0
        )

        print(
            f"  {verdict:<8}: "
            f"{count:4d} "
            f"({pct:5.1f}%)"
        )

print()


# ============================================================
# VERDICT DISTRIBUTION BY SEVERITY
# ============================================================

print("=" * 72)
print("VERDICT DISTRIBUTION BY SEVERITY")
print("=" * 72)

for severity in sorted(
    severity_data.keys(),
    key=lambda x: str(x)
):

    items = severity_data[severity]

    counts = Counter(
        get_verdict(r)
        for r in items
    )

    print()
    print(f"Severity: {severity}")
    print(f"Total   : {len(items)}")

    for verdict in [
        "VULN",
        "SMELL",
        "FP",
        "UNKNOWN"
    ]:

        count = counts.get(verdict, 0)

        pct = (
            count / len(items) * 100
            if items
            else 0
        )

        print(
            f"  {verdict:<8}: "
            f"{count:4d} "
            f"({pct:5.1f}%)"
        )

print()


# ============================================================
# TOP RULES
# ============================================================

print("=" * 72)
print("TOP RULES BY NUMBER OF FINDINGS")
print("=" * 72)

rule_counts = sorted(
    rule_data.items(),
    key=lambda x: len(x[1]),
    reverse=True
)

for rule, items in rule_counts[:20]:

    counts = Counter(
        get_verdict(r)
        for r in items
    )

    print(
        f"{len(items):4d}  "
        f"{rule}"
        f"  ["
        f"SMELL={counts.get('SMELL', 0)}, "
        f"FP={counts.get('FP', 0)}, "
        f"VULN={counts.get('VULN', 0)}, "
        f"UNKNOWN={counts.get('UNKNOWN', 0)}"
        f"]"
    )

print()


# ============================================================
# RULES WITH MOST SMELL
# ============================================================

print("=" * 72)
print("RULES WITH MOST SMELL CLASSIFICATIONS")
print("=" * 72)

smell_rules = []

for rule, items in rule_data.items():

    smell_count = sum(
        get_verdict(r) == "SMELL"
        for r in items
    )

    if smell_count:

        smell_rules.append(
            (
                rule,
                smell_count,
                len(items)
            )
        )

smell_rules.sort(
    key=lambda x: x[1],
    reverse=True
)

for rule, smell_count, rule_total in smell_rules[:20]:

    print(
        f"{smell_count:4d} SMELL / "
        f"{rule_total:4d} total  "
        f"{rule}"
    )

print()

# ============================================================
# RELIABILITY / HALLUCINATION METADATA
# ============================================================

print("=" * 72)
print("RELIABILITY / HALLUCINATION METADATA")
print("=" * 72)

print(f"Analyzed findings : {total}")

# ------------------------------------------------------------
# HUMAN REVIEW REQUIRED
# ------------------------------------------------------------

print()
print("HUMAN REVIEW REQUIRED")
print("-" * 40)

for value in [True, False, None]:

    count = human_review_counts.get(value, 0)

    if count == 0:
        continue

    pct = (
        count / total * 100
        if total
        else 0
    )

    label = (
        "True"
        if value is True
        else "False"
        if value is False
        else "Missing/None"
    )

    print(
        f"{label:<15}: "
        f"{count:4d} "
        f"({pct:5.1f}%)"
    )


# ------------------------------------------------------------
# HALLUCINATION SUSPECT
# ------------------------------------------------------------

print()
print("HALLUCINATION SUSPECT")
print("-" * 40)

for value in [True, False, None]:

    count = hallucination_suspect_counts.get(value, 0)

    if count == 0:
        continue

    pct = (
        count / total * 100
        if total
        else 0
    )

    label = (
        "True"
        if value is True
        else "False"
        if value is False
        else "Missing/None"
    )

    print(
        f"{label:<15}: "
        f"{count:4d} "
        f"({pct:5.1f}%)"
    )


# ------------------------------------------------------------
# HALLUCINATION FLAGS
# ------------------------------------------------------------

print()
print("HALLUCINATION FLAGS")
print("-" * 40)

flags_pct = (
    findings_with_hallucination_flags / total * 100
    if total
    else 0
)

print(
    f"Findings with flags : "
    f"{findings_with_hallucination_flags:4d} "
    f"({flags_pct:5.1f}%)"
)

print(
    f"Total flags         : "
    f"{total_hallucination_flags}"
)

if hallucination_flag_counts:

    print()
    print("Flag types:")

    for flag, count in hallucination_flag_counts.most_common():

        print(
            f"  {count:4d}  {flag}"
        )

else:

    print("Flag types          : None")

print()

# ============================================================
# UNKNOWN FINDINGS
# ============================================================

print("=" * 72)
print("UNKNOWN FINDINGS")
print("=" * 72)

print(
    f"Total UNKNOWN: "
    f"{len(unknown_results)}"
)

for result in unknown_results:

    print(
        f"Batch {result.get('batch_id'):>3} | "
        f"Rule: {get_rule(result)} | "
        f"Confidence: {get_confidence(result)}"
    )

print()


# ============================================================
# LOW CONFIDENCE
# ============================================================

print("=" * 72)
print(
    f"LOW-CONFIDENCE FINDINGS "
    f"(confidence <= {LOW_CONFIDENCE_THRESHOLD})"
)
print("=" * 72)

print(
    f"Total: {len(low_confidence)}"
)

for result in sorted(
    low_confidence,
    key=lambda r: (
        get_confidence(r)
        if get_confidence(r) is not None
        else 999
    )
):

    rule = get_rule(result)

    print(
        f"Batch {result.get('batch_id'):>3} | "
        f"{get_verdict(result):<7} | "
        f"confidence={get_confidence(result):.1f} | "
        f"{get_tool(rule):<10} | "
        f"{rule}"
    )

print()


# ============================================================
# EXPORT LOW-CONFIDENCE CSV
# ============================================================

with open(
    OUTPUT_CSV,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "batch_id",
        "verdict",
        "confidence",
        "tool",
        "severity",
        "rule",
    ])

    for result in low_confidence:

        rule = get_rule(result)

        writer.writerow([
            result.get("batch_id"),
            get_verdict(result),
            get_confidence(result),
            get_tool(rule),
            get_severity(result),
            rule,
        ])


# ============================================================
# FINAL SUMMARY
# ============================================================

print("=" * 72)
print("SUMMARY")
print("=" * 72)

print(
    f"Qwen3.6 findings analyzed : "
    f"{total}"
)

print(
    "Ignored batches            : 1-5"
)

print(
    "Analyzed batches           : 6-226"
)

print()

for verdict in [
    "VULN",
    "SMELL",
    "FP",
    "UNKNOWN"
]:

    print(
        f"{verdict:<8}: "
        f"{verdict_counts.get(verdict, 0)}"
    )

if confidences:

    print(
        f"Average confidence        : "
        f"{sum(confidences)/len(confidences):.3f}/10"
    )

print(
    f"Vote consistency          : "
    f"{consistency_pct:.1f}%"
)

print(
    f"Low-confidence findings   : "
    f"{len(low_confidence)}"
)

print()

print(
    f"Low-confidence CSV        : "
    f"{OUTPUT_CSV}"
)

print()

print("Analysis complete.")
