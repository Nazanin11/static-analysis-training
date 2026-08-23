#!/usr/bin/env python3

import json
import math
import os
import requests

SONAR_URL = "http://localhost:9000"
PROJECT_KEY = "bird-2.17.1-scoped"

OUTPUT_FILE = (
    "reports/sonarqube/"
    "sonarqube-security-reliability.json"
)

PAGE_SIZE = 500


def get_all_issues():

    url = f"{SONAR_URL}/api/issues/search"

    params = {
        "componentKeys": PROJECT_KEY,
        "ps": PAGE_SIZE,
        "p": 1,
    }

    print("=" * 60)
    print("SonarQube Security / Reliability Export")
    print("=" * 60)

    response = requests.get(
        url,
        params=params,
        auth=(os.environ["SONAR_TOKEN"], ""),
    )

    response.raise_for_status()

    first_page = response.json()

    total = first_page.get("total", 0)
    pages = math.ceil(total / PAGE_SIZE)

    print(f"[INFO] Total SonarQube issues: {total}")
    print(f"[INFO] Pages to fetch: {pages}")

    all_issues = []

    for page in range(1, pages + 1):

        print(f"[FETCH] Page {page}/{pages}")

        params = {
            "componentKeys": PROJECT_KEY,
            "ps": PAGE_SIZE,
            "p": page,
        }

        response = requests.get(
            url,
            params=params,
            auth=(os.environ["SONAR_TOKEN"], ""),
        )

        response.raise_for_status()

        data = response.json()

        issues = data.get("issues", [])

        all_issues.extend(issues)

        print(f"        Retrieved: {len(issues)}")

    print(f"[INFO] All issues retrieved: {len(all_issues)}")

    return all_issues


def filter_findings(issues):

    findings = []

    removed_maintainability = 0
    removed_other = 0

    for issue in issues:

        impacts = issue.get("impacts", [])

        qualities = {
            impact.get("softwareQuality")
            for impact in impacts
            if impact.get("softwareQuality")
        }

        # --------------------------------------------------
        # Keep SECURITY
        # --------------------------------------------------

        if "SECURITY" in qualities:

            finding = dict(issue)
            finding["category"] = "SECURITY"

            findings.append(finding)

            continue

        # --------------------------------------------------
        # Keep RELIABILITY
        # --------------------------------------------------

        if "RELIABILITY" in qualities:

            finding = dict(issue)
            finding["category"] = "RELIABILITY"

            findings.append(finding)

            continue

        # --------------------------------------------------
        # Remove MAINTAINABILITY
        # --------------------------------------------------

        if "MAINTAINABILITY" in qualities:

            removed_maintainability += 1

            continue

        removed_other += 1

    return (
        findings,
        removed_maintainability,
        removed_other,
    )


def main():

    issues = get_all_issues()

    (
        findings,
        removed_maintainability,
        removed_other,
    ) = filter_findings(issues)

    security = sum(
        1
        for finding in findings
        if finding.get("category") == "SECURITY"
    )

    reliability = sum(
        1
        for finding in findings
        if finding.get("category") == "RELIABILITY"
    )

    output = {
        "project": PROJECT_KEY,
        "summary": {
            "security": security,
            "reliability": reliability,
            "total": len(findings),
            "removed_maintainability": removed_maintainability,
            "removed_other": removed_other,
        },
        "findings": findings,
    }

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("=" * 60)
    print("[DONE]")
    print("=" * 60)

    print(f"Output: {OUTPUT_FILE}")
    print()
    print(f"Security:              {security}")
    print(f"Reliability:           {reliability}")
    print(f"Total:                 {len(findings)}")
    print(f"Removed MAINTAINABILITY: {removed_maintainability}")
    print(f"Removed other:           {removed_other}")


if __name__ == "__main__":
    main()
