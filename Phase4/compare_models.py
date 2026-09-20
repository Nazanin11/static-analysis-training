import json
import csv
from collections import Counter, defaultdict

# ============================================================
# Configuration
# ============================================================

QWEN36_FILE = "llm_triage_results_Pilot_Qwen3.6.json"
QWEN38_FILE = "llm_triage_results_Pilot_Qwen3.8.json"

START_BATCH = 11
END_BATCH = 140

DISAGREEMENTS_CSV = "model_disagreements_11_140.csv"


# ============================================================
# Load results
# ============================================================

def load_results(filename):

    with open(filename, "r") as f:
        data = json.load(f)

    results = {}

    for batch in data:

        batch_id = batch.get("batch_id")

        if not (START_BATCH <= batch_id <= END_BATCH):
            continue

        verdicts = batch.get("verdict_array", [])

        if not verdicts:
            continue

        v = verdicts[0]

        results[batch_id] = {
            "batch_id": batch_id,
            "file": batch.get("file", ""),
            "rule": v.get("pattern_name", ""),
            "verdict": v.get("verdict", "UNKNOWN"),
            "confidence": v.get("confidence"),
        }

    return results


qwen36 = load_results(QWEN36_FILE)
qwen38 = load_results(QWEN38_FILE)

common_ids = sorted(set(qwen36) & set(qwen38))


# ============================================================
# Helper functions
# ============================================================

def percentage(value, total):

    if total == 0:
        return 0.0

    return value / total * 100


def get_tool(rule):

    rule_lower = rule.lower()

    if "codeql" in rule_lower:
        return "CodeQL"

    if "semgrep" in rule_lower:
        return "Semgrep"

    if "cppcheck" in rule_lower:
        return "Cppcheck"

    if rule_lower.startswith("c:"):
        return "SonarQube"

    return "Other"


def confidence_bucket(value):

    if not isinstance(value, (int, float)):
        return "UNKNOWN"

    if value <= 3:
        return "1-3"

    if value <= 6:
        return "4-6"

    if value <= 8:
        return "7-8"

    return "9-10"


# ============================================================
# Basic information
# ============================================================

print("=" * 72)
print("QWEN3.6 vs QWEN3.8 — STATISTICAL COMPARISON")
print("=" * 72)

print(f"Comparison range : Batch {START_BATCH}-{END_BATCH}")
print(f"Qwen3.6 findings : {len(qwen36)}")
print(f"Qwen3.8 findings : {len(qwen38)}")
print(f"Common findings  : {len(common_ids)}")


# ============================================================
# Verdict statistics
# ============================================================

def print_verdict_stats(name, results):

    print("\n" + "=" * 72)
    print(name)
    print("=" * 72)

    total = len(results)

    print(f"Total findings: {total}\n")

    counts = Counter(
        r["verdict"]
        for r in results.values()
    )

    for verdict in ["VULN", "SMELL", "FP", "UNKNOWN"]:

        count = counts.get(verdict, 0)

        print(
            f"{verdict:8} : "
            f"{count:3} "
            f"({percentage(count, total):5.1f}%)"
        )

    confidences = [
        r["confidence"]
        for r in results.values()
        if isinstance(r["confidence"], (int, float))
    ]

    if confidences:

        print("\nConfidence (scale 1-10)")

        print(f"Average : {sum(confidences)/len(confidences):.3f}")
        print(f"Minimum : {min(confidences):.1f}")
        print(f"Maximum : {max(confidences):.1f}")

        buckets = Counter(
            confidence_bucket(c)
            for c in confidences
        )

        print("\nConfidence distribution:")

        for bucket in ["1-3", "4-6", "7-8", "9-10"]:

            count = buckets.get(bucket, 0)

            print(
                f"{bucket:6} : "
                f"{count:3} "
                f"({percentage(count, len(confidences)):5.1f}%)"
            )


print_verdict_stats("Qwen3.6", qwen36)
print_verdict_stats("Qwen3.8", qwen38)


# ============================================================
# Direct comparison
# ============================================================

same = 0
different = 0

matrix = Counter()
disagreements = []

for batch_id in common_ids:

    a = qwen36[batch_id]
    b = qwen38[batch_id]

    v36 = a["verdict"]
    v38 = b["verdict"]

    matrix[(v36, v38)] += 1

    if v36 == v38:

        same += 1

    else:

        different += 1

        disagreements.append({
            "batch_id": batch_id,
            "file": a["file"],
            "rule": a["rule"],
            "tool": get_tool(a["rule"]),
            "Qwen3.6_verdict": v36,
            "Qwen3.8_verdict": v38,
            "Qwen3.6_confidence": a["confidence"],
            "Qwen3.8_confidence": b["confidence"],
        })


total = len(common_ids)


print("\n" + "=" * 72)
print("DIRECT AGREEMENT")
print("=" * 72)

print(f"Common findings : {total}")
print(f"Same verdict    : {same} ({percentage(same, total):.1f}%)")
print(f"Different       : {different} ({percentage(different, total):.1f}%)")


# ============================================================
# Agreement matrix
# ============================================================

labels = ["VULN", "SMELL", "FP", "UNKNOWN"]

print("\n" + "=" * 72)
print("VERDICT AGREEMENT MATRIX")
print("Rows    = Qwen3.6 verdict")
print("Columns = Qwen3.8 verdict")
print("=" * 72)

print(f"{'Qwen3.6 / Qwen3.8':20}", end="")

for label in labels:
    print(f"{label:10}", end="")

print()

for x in labels:

    print(f"{x:12}", end="")

    for y in labels:

        print(
            f"{matrix[(x, y)]:10}",
            end=""
        )

    print()


# ============================================================
# Disagreement direction
# ============================================================

direction_counts = Counter(
    f"{d['Qwen3.6_verdict']} -> {d['Qwen3.8_verdict']}"
    for d in disagreements
)


print("\n" + "=" * 72)
print("DISAGREEMENT DIRECTIONS")
print("Format: Qwen3.6 verdict -> Qwen3.8 verdict")
print("=" * 72)

for direction, count in direction_counts.most_common():

    print(
        f"{direction:20} : "
        f"{count:3} "
        f"({percentage(count, different):5.1f}%)"
    )


# ============================================================
# Disagreements by tool
# ============================================================

tool_counts = Counter(
    d["tool"]
    for d in disagreements
)


print("\n" + "=" * 72)
print("DISAGREEMENTS BY TOOL")
print("Counts refer to findings where Qwen3.6 and Qwen3.8 disagreed.")
print("=" * 72)

for tool, count in tool_counts.most_common():

    print(
        f"{tool:12} : "
        f"{count:3} "
        f"({percentage(count, different):5.1f}%)"
    )


# ============================================================
# Disagreements by tool + direction
# ============================================================

tool_direction = Counter(
    (
        d["tool"],
        f"{d['Qwen3.6_verdict']} -> {d['Qwen3.8_verdict']}"
    )
    for d in disagreements
)


print("\n" + "=" * 72)
print("DISAGREEMENTS BY TOOL AND DIRECTION")
print("Direction: Qwen3.6 verdict -> Qwen3.8 verdict")
print("=" * 72)

for (tool, direction), count in tool_direction.most_common():

    print(
        f"{tool:12} | "
        f"{direction:20} : "
        f"{count}"
    )


# ============================================================
# Disagreements by rule
# ============================================================

rule_counts = Counter(
    d["rule"]
    for d in disagreements
)


print("\n" + "=" * 72)
print("TOP RULES WITH MOST DISAGREEMENTS")
print("=" * 72)

for rule, count in rule_counts.most_common():

    print(f"{count:3}  {rule}")


# ============================================================
# Confidence comparison
# ============================================================

paired = []

for batch_id in common_ids:

    c36 = qwen36[batch_id]["confidence"]
    c38 = qwen38[batch_id]["confidence"]

    if (
        isinstance(c36, (int, float))
        and isinstance(c38, (int, float))
    ):
        paired.append((c36, c38))


print("\n" + "=" * 72)
print("CONFIDENCE COMPARISON")
print("Confidence scale: 1-10")
print("=" * 72)

if paired:

    avg36 = sum(x[0] for x in paired) / len(paired)
    avg38 = sum(x[1] for x in paired) / len(paired)

    print(f"Paired findings : {len(paired)}")
    print(f"Qwen3.6 average confidence : {avg36:.3f}/10")
    print(f"Qwen3.8 average confidence : {avg38:.3f}/10")
    print(f"Difference (Qwen3.6 - Qwen3.8): {avg36 - avg38:+.3f}")

# ============================================================
# Confidence on disagreements
# ============================================================

dis_conf36 = [
    d["Qwen3.6_confidence"]
    for d in disagreements
    if isinstance(d["Qwen3.6_confidence"], (int, float))
]

dis_conf38 = [
    d["Qwen3.8_confidence"]
    for d in disagreements
    if isinstance(d["Qwen3.8_confidence"], (int, float))
]


print("\n" + "=" * 72)
print("CONFIDENCE ON DISAGREEMENTS")
print("Only findings where the two models produced different verdicts.")
print("=" * 72)

if dis_conf36 and dis_conf38:

    avg36 = sum(dis_conf36) / len(dis_conf36)
    avg38 = sum(dis_conf38) / len(dis_conf38)

    print(f"Qwen3.6 average confidence : {avg36:.3f}/10")
    print(f"Qwen3.8 average confidence : {avg38:.3f}/10")
    print(f"Difference (Qwen3.6 - Qwen3.8): {avg36 - avg38:+.3f}")

# ============================================================
# Vote consistency
# ============================================================

def vote_consistency(filename):

    with open(filename, "r") as f:
        data = json.load(f)

    total = 0
    consistent = 0
    inconsistent = 0

    for batch in data:

        bid = batch.get("batch_id")

        if not (START_BATCH <= bid <= END_BATCH):
            continue

        votes = batch.get("verdict_array", [])

        if not votes:
            continue

        verdicts = [
            v.get("verdict", "UNKNOWN")
            for v in votes
        ]

        total += 1

        if len(set(verdicts)) == 1:
            consistent += 1
        else:
            inconsistent += 1

    return total, consistent, inconsistent


for name, filename in [
    ("Qwen3.6", QWEN36_FILE),
    ("Qwen3.8", QWEN38_FILE),
]:

    total_v, consistent, inconsistent = vote_consistency(filename)

    print("\n" + "=" * 72)
    print(f"{name} VOTE CONSISTENCY")
    print("=" * 72)

    print(f"Findings     : {total_v}")
    print(f"Consistent   : {consistent}")
    print(f"Inconsistent : {inconsistent}")

    if total_v:

        print(
            f"Consistency  : "
            f"{percentage(consistent, total_v):.1f}%"
        )


# ============================================================
# Export disagreements
# ============================================================

with open(DISAGREEMENTS_CSV, "w", newline="") as f:

    fieldnames = [
        "batch_id",
        "file",
        "rule",
        "tool",
        "Qwen3.6_verdict",
        "Qwen3.8_verdict",
        "Qwen3.6_confidence",
        "Qwen3.8_confidence",
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(disagreements)


# ============================================================
# Final summary
# ============================================================

print("\n" + "=" * 72)
print("SUMMARY")
print("=" * 72)

print(f"Shared findings       : {total}")
print(f"Agreement              : {same} ({percentage(same, total):.1f}%)")
print(f"Disagreement           : {different} ({percentage(different, total):.1f}%)")
print(f"Disagreement CSV       : {DISAGREEMENTS_CSV}")

print("\nAnalysis complete.")
