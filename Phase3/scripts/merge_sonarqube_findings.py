#!/usr/bin/env python3

import json
import os

ISSUES_FILE = "reports/sonarqube/sonarqube-security-reliability.json"
HOTSPOTS_FILE = "reports/sonarqube/sonarqube-hotspots.json"
OUTPUT_FILE = "reports/sonarqube/merged_candidates.json"

PROJECT = "bird-2.17.1-scoped"


def main():

    # Load Security / Reliability findings
    with open(ISSUES_FILE, encoding="utf-8") as f:
        issues = json.load(f)

    # Load Security Hotspots
    with open(HOTSPOTS_FILE, encoding="utf-8") as f:
        hotspots = json.load(f)

    findings = []

    # --------------------------------------------------
    # Security / Reliability findings
    # --------------------------------------------------

    for issue in issues.get("findings", []):
        findings.append(dict(issue))

    # --------------------------------------------------
    # Security Hotspots
    # --------------------------------------------------

    for hotspot in hotspots.get("hotspots", []):

        finding = dict(hotspot)

        finding["type"] = "SECURITY_HOTSPOT"
        finding["category"] = "SECURITY"

        findings.append(finding)

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    bugs = sum(
        1
        for f in findings
        if f.get("type") == "BUG"
    )

    vulnerabilities = sum(
        1
        for f in findings
        if f.get("type") == "VULNERABILITY"
    )

    security_hotspots = sum(
        1
        for f in findings
        if f.get("type") == "SECURITY_HOTSPOT"
    )

    reliability = sum(
        1
        for f in findings
        if f.get("category") == "RELIABILITY"
    )

    security = sum(
        1
        for f in findings
        if f.get("category") == "SECURITY"
        and f.get("type") != "SECURITY_HOTSPOT"
    )

    output = {
        "project": PROJECT,
        "summary": {
            "reliability": reliability,
            "security": security,
            "bugs": bugs,
            "vulnerabilities": vulnerabilities,
            "security_hotspots": security_hotspots,
            "total": len(findings)
        },
        "findings": findings
    }

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("=" * 60)
    print("SonarQube Findings Export and Merge")
    print("=" * 60)
    print(f"Output: {OUTPUT_FILE}")
    print()
    print(f"Reliability:       {reliability}")
    print(f"Security:          {security}")
    print(f"BUGs:              {bugs}")
    print(f"Vulnerabilities:   {vulnerabilities}")
    print(f"Security Hotspots: {security_hotspots}")
    print(f"Total:             {len(findings)}")


if __name__ == "__main__":
    main()
