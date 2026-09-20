#!/usr/bin/env python3

import json
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path("reports/sonarqube/merged_candidates.json")

CODEQL_RULES_FILE = Path(
    "/home/nazanin/rules/reports/codeql/cpp-security-experimental-rules.json"
)

OUTPUT_FILE = Path(
    "reports/sonarqube/merged_candidates_with_cwe.json"
)


# ============================================================
# Load CodeQL Rule Metadata
# ============================================================

with CODEQL_RULES_FILE.open("r", encoding="utf-8") as f:
    codeql_data = json.load(f)

queries = codeql_data.get("queries", [])

# Build:
# cpp/unbounded-write -> ["CWE-120", "CWE-787", "CWE-805"]
codeql_cwe_map = {
    query["id"]: query.get("cwe", [])
    for query in queries
    if query.get("id")
}


# ============================================================
# Load Findings
# ============================================================

with INPUT_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)


if isinstance(data, dict):
    findings = data.get("findings", [])
else:
    findings = data


# ============================================================
# Add CWE to CodeQL Findings
# ============================================================

total_findings = len(findings)
codeql_findings = 0
mapped_findings = 0
unmapped_findings = 0

for finding in findings:

    rule = finding.get("rule", "")

    # Only process CodeQL findings
    if not rule.startswith("external_CodeQL:"):
        continue

    codeql_findings += 1

    # Convert:
    # external_CodeQL:cpp/unbounded-write
    #
    # to:
    # cpp/unbounded-write

    query_id = rule.removeprefix("external_CodeQL:")

    cwe = codeql_cwe_map.get(query_id)

    if cwe:
        finding["cwe"] = cwe
        mapped_findings += 1
    else:
        # Query exists but has no CWE,
        # or the query was not found in the rule metadata.
        finding["cwe"] = []
        unmapped_findings += 1


# ============================================================
# Save Output
# ============================================================

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)


# ============================================================
# Summary
# ============================================================

print("=" * 60)
print("CodeQL CWE Enrichment")
print("=" * 60)

print(f"Total findings:          {total_findings}")
print(f"CodeQL findings:         {codeql_findings}")
print(f"CodeQL with CWE:         {mapped_findings}")
print(f"CodeQL without CWE:      {unmapped_findings}")

print()
print(f"CodeQL queries:          {len(queries)}")
print(
    f"Queries with CWE:        "
    f"{sum(1 for q in queries if q.get('cwe'))}"
)
print(
    f"Queries without CWE:     "
    f"{sum(1 for q in queries if not q.get('cwe'))}"
)

print()
print(f"Output: {OUTPUT_FILE}")
print("=" * 60)#!/usr/bin/env python3

import json
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path("reports/sonarqube/merged_candidates.json")

CODEQL_RULES_FILE = Path(
    "reports/codeql/cpp-security-experimental-rules.json"
)

OUTPUT_FILE = Path(
    "reports/sonarqube/merged_candidates_with_cwe.json"
)


# ============================================================
# Load CodeQL Rule Metadata
# ============================================================

with CODEQL_RULES_FILE.open("r", encoding="utf-8") as f:
    codeql_data = json.load(f)

queries = codeql_data.get("queries", [])

# Build:
# cpp/unbounded-write -> ["CWE-120", "CWE-787", "CWE-805"]
codeql_cwe_map = {
    query["id"]: query.get("cwe", [])
    for query in queries
    if query.get("id")
}


# ============================================================
# Load Findings
# ============================================================

with INPUT_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)


if isinstance(data, dict):
    findings = data.get("findings", [])
else:
    findings = data


# ============================================================
# Add CWE to CodeQL Findings
# ============================================================

total_findings = len(findings)
codeql_findings = 0
mapped_findings = 0
unmapped_findings = 0

for finding in findings:

    rule = finding.get("rule", "")

    # Only process CodeQL findings
    if not rule.startswith("external_CodeQL:"):
        continue

    codeql_findings += 1

    # Convert:
    # external_CodeQL:cpp/unbounded-write
    #
    # to:
    # cpp/unbounded-write

    query_id = rule.removeprefix("external_CodeQL:")

    cwe = codeql_cwe_map.get(query_id)

    if cwe:
        finding["cwe"] = cwe
        mapped_findings += 1
    else:
        # Query exists but has no CWE,
        # or the query was not found in the rule metadata.
        finding["cwe"] = []
        unmapped_findings += 1


# ============================================================
# Save Output
# ============================================================

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)


# ============================================================
# Summary
# ============================================================

print("=" * 60)
print("CodeQL CWE Enrichment")
print("=" * 60)

print(f"Total findings:          {total_findings}")
print(f"CodeQL findings:         {codeql_findings}")
print(f"CodeQL with CWE:         {mapped_findings}")
print(f"CodeQL without CWE:      {unmapped_findings}")

print()
print(f"CodeQL queries:          {len(queries)}")
print(
    f"Queries with CWE:        "
    f"{sum(1 for q in queries if q.get('cwe'))}"
)
print(
    f"Queries without CWE:     "
    f"{sum(1 for q in queries if not q.get('cwe'))}"
)

print()
print(f"Output: {OUTPUT_FILE}")
print("=" * 60)
