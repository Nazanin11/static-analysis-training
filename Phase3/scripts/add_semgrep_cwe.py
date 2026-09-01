#!/usr/bin/env python3

import json
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path(
    "reports/sonarqube/merged_candidates_with_cwe.json"
)

RULES_FILE = Path(
    "/home/nazanin/rules/semgrep/semgrep-c-rules.json"
)

OUTPUT_FILE = Path(
    "reports/sonarqube/merged_candidates_with_cwe.json"
)


# ============================================================
# Helpers
# ============================================================

def extract_semgrep_rule_id(rule: str) -> str | None:
    """
    Extract the original Semgrep rule ID from a merged finding.

    Example:
        external_Semgrep:c.lang.security.double-free.double-free

    Returns:
        double-free
    """

    prefix = "external_Semgrep:"

    if not rule.startswith(prefix):
        return None

    rule_path = rule[len(prefix):]

    # The final component is the original Semgrep rule ID.
    return rule_path.split(".")[-1]


def normalize_cwes(cwe_data) -> list[str]:
    """
    Normalize CWE metadata.

    Example:
        'CWE-415: Double Free'
        ->
        'CWE-415'
    """

    if not cwe_data:
        return []

    if isinstance(cwe_data, str):
        cwe_data = [cwe_data]

    cwes = []

    for item in cwe_data:
        if not isinstance(item, str):
            continue

        # Keep only the CWE identifier.
        cwe_id = item.split(":", 1)[0].strip()

        if cwe_id.startswith("CWE-"):
            cwes.append(cwe_id)

    return sorted(set(cwes))


# ============================================================
# Main
# ============================================================

def main() -> None:

    print("=" * 60)
    print("Semgrep CWE Enrichment")
    print("=" * 60)

    # --------------------------------------------------------
    # Validate files
    # --------------------------------------------------------

    if not INPUT_FILE.exists():
        print(f"[ERROR] Input file not found: {INPUT_FILE}")
        return

    if not RULES_FILE.exists():
        print(f"[ERROR] Semgrep rules file not found: {RULES_FILE}")
        return

    # --------------------------------------------------------
    # Load findings
    # --------------------------------------------------------

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    findings = data.get("findings", [])

    print(f"Total findings: {len(findings)}")

    # --------------------------------------------------------
    # Load Semgrep rule metadata
    # --------------------------------------------------------

    with RULES_FILE.open(
        "r",
        encoding="utf-8",
    ) as f:
        semgrep_rules = json.load(f)

    # --------------------------------------------------------
    # Build rule -> CWE mapping
    # --------------------------------------------------------

    rule_cwe_map: dict[str, list[str]] = {}

    for rule in semgrep_rules:

        rule_id = rule.get("id")

        if not rule_id:
            continue

        cwes = normalize_cwes(
            rule.get("cwe")
        )

        rule_cwe_map[rule_id] = cwes

    # --------------------------------------------------------
    # Find Semgrep findings
    # --------------------------------------------------------

    semgrep_findings = [
        finding
        for finding in findings
        if (
            finding.get("externalRuleEngine") == "Semgrep"
            and finding.get("rule", "").startswith(
                "external_Semgrep:"
            )
        )
    ]

    semgrep_rules_used = sorted(
        {
            extract_semgrep_rule_id(
                finding.get("rule", "")
            )
            for finding in semgrep_findings
        }
        - {None}
    )

    print(
        f"Semgrep findings:      {len(semgrep_findings)}"
    )

    print(
        f"Unique Semgrep rules:  {len(semgrep_rules_used)}"
    )

    # --------------------------------------------------------
    # Resolve CWE metadata
    # --------------------------------------------------------

    rules_with_cwe = 0
    rules_without_cwe = 0

    print("\nResolving Semgrep rules:")
    print("-" * 60)

    for rule_id in semgrep_rules_used:

        cwes = rule_cwe_map.get(
            rule_id,
            []
        )

        if cwes:
            rules_with_cwe += 1

            print(
                f"{rule_id:45} -> "
                f"{', '.join(cwes)}"
            )

        else:
            rules_without_cwe += 1

            print(
                f"{rule_id:45} -> NO CWE"
            )

    # --------------------------------------------------------
    # Enrich findings
    # --------------------------------------------------------

    enriched_findings = []

    semgrep_with_cwe = 0
    semgrep_without_cwe = 0

    for finding in findings:

        enriched = dict(finding)

        rule = finding.get(
            "rule",
            ""
        )

        is_semgrep = (
            finding.get("externalRuleEngine")
            == "Semgrep"
            and rule.startswith(
                "external_Semgrep:"
            )
        )

        if is_semgrep:

            rule_id = extract_semgrep_rule_id(
                rule
            )

            cwes = rule_cwe_map.get(
                rule_id,
                []
            )

            enriched["cwe"] = cwes

            if cwes:
                semgrep_with_cwe += 1
            else:
                semgrep_without_cwe += 1

        enriched_findings.append(
            enriched
        )

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    output_data = dict(data)

    output_data["findings"] = (
        enriched_findings
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output_data,
            f,
            indent=2,
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("Enrichment completed")
    print("=" * 60)

    print(
        f"Total findings:          {len(findings)}"
    )

    print(
        f"Semgrep findings:        {len(semgrep_findings)}"
    )

    print(
        f"Semgrep with CWE:        {semgrep_with_cwe}"
    )

    print(
        f"Semgrep without CWE:     {semgrep_without_cwe}"
    )

    print()

    print(
        f"Semgrep rules:           {len(semgrep_rules_used)}"
    )

    print(
        f"Rules with CWE:          {rules_with_cwe}"
    )

    print(
        f"Rules without CWE:       {rules_without_cwe}"
    )

    print()

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
