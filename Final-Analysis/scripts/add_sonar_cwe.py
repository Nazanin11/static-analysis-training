#!/usr/bin/env python3

import json
import os
import re
import subprocess
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path(
    "reports/sonarqube/merged_candidates_with_cwe.json"
)

OUTPUT_FILE = Path(
    "reports/sonarqube/merged_candidates_with_cwe.json"
)

SONAR_URL = "http://localhost:9000"


# ============================================================
# Helpers
# ============================================================

def get_sonar_rule(rule_key: str) -> dict:
    """
    Retrieve SonarQube rule metadata using the SonarQube API.
    """

    token = os.environ.get("SONAR_TOKEN")

    if not token:
        raise RuntimeError(
            "SONAR_TOKEN environment variable is not set."
        )

    result = subprocess.run(
        [
            "curl",
            "-s",
            "-u",
            f"{token}:",
            f"{SONAR_URL}/api/rules/show?key={rule_key}",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    if not result.stdout.strip():
        raise RuntimeError(
            f"Empty response from SonarQube for rule {rule_key}"
        )

    data = json.loads(result.stdout)

    return data.get("rule", {})


def extract_cwes(rule_data: dict) -> list[str]:
    """
    Extract CWE identifiers from SonarQube rule descriptionSections.
    """

    sections = rule_data.get("descriptionSections", [])

    content = "\n".join(
        section.get("content", "")
        for section in sections
        if isinstance(section, dict)
    )

    cwes = sorted(
        {
            f"CWE-{number}"
            for number in re.findall(
                r"\bCWE-(\d+)\b",
                content,
                re.IGNORECASE,
            )
        },
        key=lambda x: int(x.split("-")[1]),
    )

    return cwes


# ============================================================
# Main
# ============================================================

def main() -> None:

    print("=" * 60)
    print("SonarQube CWE Enrichment")
    print("=" * 60)

    if not INPUT_FILE.exists():
        print(f"[ERROR] Input file not found: {INPUT_FILE}")
        return

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    findings = data.get("findings", [])

    print(f"Total findings: {len(findings)}")

    # --------------------------------------------------------
    # Collect unique SonarQube rules
    # --------------------------------------------------------

    sonar_findings = [
        finding
        for finding in findings
        if (
            finding.get("externalRuleEngine") is None
            and (
                finding.get("rule", "").startswith("c:")
                or finding.get("ruleKey", "").startswith("c:")
            )
        )
    ]

    sonar_rules = sorted(
        {
            finding.get("rule") or finding.get("ruleKey")
            for finding in sonar_findings
            if finding.get("rule") or finding.get("ruleKey")
        }
    )
    print(f"SonarQube findings: {len(sonar_findings)}")
    print(f"Unique Sonar rules: {len(sonar_rules)}")

    # --------------------------------------------------------
    # Retrieve CWE metadata
    # --------------------------------------------------------

    rule_cwe_map: dict[str, list[str]] = {}

    rules_with_cwe = 0
    rules_without_cwe = 0

    print("\nResolving SonarQube rules:")
    print("-" * 60)

    for rule_key in sonar_rules:

        try:
            rule_data = get_sonar_rule(rule_key)

            cwes = extract_cwes(rule_data)

            rule_cwe_map[rule_key] = cwes

            if cwes:
                rules_with_cwe += 1
                print(
                    f"{rule_key:10} -> "
                    f"{', '.join(cwes)}"
                )
            else:
                rules_without_cwe += 1
                print(
                    f"{rule_key:10} -> NO CWE"
                )

        except Exception as exc:

            print(
                f"{rule_key:10} -> ERROR: {exc}"
            )

            # Do not guess CWE information.
            rule_cwe_map[rule_key] = []

    # --------------------------------------------------------
    # Enrich findings
    # --------------------------------------------------------

    enriched_findings = []

    sonar_with_cwe = 0
    sonar_without_cwe = 0

    for finding in findings:

        # Copy the original finding.
        enriched = dict(finding)

        rule_engine = finding.get(
            "externalRuleEngine"
                )
        rule_key = (
            finding.get("rule")
            or finding.get("ruleKey")
            or ""
        )

        is_sonar = (
            rule_engine is None
            and rule_key.startswith("c:")
        )

        if is_sonar:

            cwes = rule_cwe_map.get(
                rule_key,
                []
            )

            enriched["cwe"] = cwes

            if cwes:
                sonar_with_cwe += 1
            else:
                sonar_without_cwe += 1

        enriched_findings.append(enriched)

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    output_data = dict(data)

    output_data["findings"] = enriched_findings

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
        f"SonarQube findings:      {len(sonar_findings)}"
    )

    print(
        f"SonarQube with CWE:      {sonar_with_cwe}"
    )

    print(
        f"SonarQube without CWE:   {sonar_without_cwe}"
    )

    print()

    print(
        f"Sonar rules:             {len(sonar_rules)}"
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
