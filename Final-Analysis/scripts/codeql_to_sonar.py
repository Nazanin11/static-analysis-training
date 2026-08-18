#!/usr/bin/env python3

import json
import os
import sys


def map_severity(level):
    level = (level or "").lower()

    mapping = {
        "error": "CRITICAL",
        "warning": "MAJOR",
        "recommendation": "MINOR",
        "note": "INFO",
        "none": "INFO"
    }

    return mapping.get(level, "MAJOR")

if len(sys.argv) != 3:
    print("Usage:")
    print("python3 codeql_to_sonar.py input.sarif output.json")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, encoding="utf-8") as f:
    sarif = json.load(f)

run = sarif["runs"][0]

driver = run["tool"]["driver"]

rules = {}

for rule in driver.get("rules", []):

    rule_id = rule["id"]

    desc = ""

    if "fullDescription" in rule:
        desc = rule["fullDescription"].get("text", "")

    elif "shortDescription" in rule:
        desc = rule["shortDescription"].get("text", "")

    severity = map_severity(
        rule.get("defaultConfiguration", {}).get("level")
    )

    rules[rule_id] = {
        "id": rule_id,
        "name": rule.get("name", rule_id),
        "description": desc,
        "engineId": "CodeQL",
        "cleanCodeAttribute": "TRUSTWORTHY",
        "type": "VULNERABILITY",
        "severity": severity
    }


issues = []

for result in run.get("results", []):

    if not result.get("locations"):
        continue

    location = result["locations"][0]["physicalLocation"]

    artifact = location.get("artifactLocation", {})

    region = location.get("region", {})

    start_line = region.get("startLine", 1)
    end_line = region.get("endLine", start_line)

    rule_id = result.get("ruleId", "UNKNOWN")

    level = map_severity(result.get("level"))

    if rule_id not in rules:

        rules[rule_id] = {
            "id": rule_id,
            "name": rule_id,
            "description": "",
            "engineId": "CodeQL",
            "cleanCodeAttribute": "TRUSTWORTHY",
            "type": "VULNERABILITY",
            "severity": level
        }

    message = result.get("message", {}).get("text", "")

    issues.append(
        {
            "ruleId": rule_id,
            "primaryLocation": {
                "message": message,
                "filePath": artifact.get("uri", ""),
                "textRange": {
                    "startLine": start_line,
                    "endLine": end_line
                }
            }
        }
    )


sonar = {
    "rules": list(rules.values()),
    "issues": issues
}

os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(sonar, f, indent=2)

print(f"Rules : {len(rules)}")
print(f"Issues: {len(issues)}")
print(f"Saved : {output_file}")
