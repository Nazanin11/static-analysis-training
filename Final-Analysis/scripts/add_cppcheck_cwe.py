#!/usr/bin/env python3

import json
from pathlib import Path

FINDINGS_FILE = Path(
    "reports/sonarqube/merged_candidates_with_cwe.json"
)

RULES_FILE = Path(
    "/home/nazanin/rules/cppcheck/cppcheck-rules.json"
)

OUTPUT_FILE = Path(
    "reports/sonarqube/merged_candidates_with_cwe.json"
)


def normalize_cwe(value):
    """Convert Cppcheck CWE value to a consistent list format."""

    if not value:
        return []

    if isinstance(value, list):
        values = value
    else:
        values = [value]

    result = []

    for cwe in values:
        cwe = str(cwe).strip()

        if not cwe:
            continue

        if cwe.upper().startswith("CWE-"):
            result.append(cwe.upper())
        else:
            result.append(f"CWE-{cwe}")

    return result


def main():

    print("=" * 60)
    print("Cppcheck CWE Enrichment")
    print("=" * 60)

    with FINDINGS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    with RULES_FILE.open("r", encoding="utf-8") as f:
        rules_data = json.load(f)

    findings = data["findings"]
    rules = rules_data["rules"]

    # Build:
    # Cppcheck Check ID -> CWE
    rule_cwe = {
        rule["id"]: normalize_cwe(rule.get("cwe"))
        for rule in rules
    }

    cppcheck_findings = [
        f for f in findings
        if f.get("externalRuleEngine") == "Cppcheck"
    ]

    matched = 0
    with_cwe = 0
    without_cwe = 0

    for finding in cppcheck_findings:

        rule = finding.get("rule", "")

        prefix = "external_Cppcheck:"

        if not rule.startswith(prefix):
            without_cwe += 1
            continue

        check_id = rule[len(prefix):]

        cwes = rule_cwe.get(check_id)

        if cwes:
            finding["cwe"] = cwes
            matched += 1
            with_cwe += 1
        else:
            finding["cwe"] = []
            without_cwe += 1

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Total findings:          {len(findings)}")
    print(f"Cppcheck findings:      {len(cppcheck_findings)}")
    print(f"Cppcheck with CWE:      {with_cwe}")
    print(f"Cppcheck without CWE:   {without_cwe}")
    print(f"Matched rules:           {matched}")
    print()
    print(f"Cppcheck rules:          {len(rules)}")
    print(f"Rules with CWE:          {sum(bool(v) for v in rule_cwe.values())}")
    print(f"Rules without CWE:       {sum(not bool(v) for v in rule_cwe.values())}")
    print()
    print(f"Output: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
