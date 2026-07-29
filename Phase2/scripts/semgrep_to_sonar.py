#!/usr/bin/env python3

import json
import os
import sys

def map_severity(level):
    level = (level or "").lower()

    mapping = {
        "error": "CRITICAL",
        "warning": "MAJOR",
        "note": "INFO",
        "none": "INFO"
    }

    return mapping.get(level, "MAJOR")


if len(sys.argv) != 4:
    print("Usage:")
    print("python3 sarif_to_sonar.py input.sarif output.json ENGINE_NAME")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]
engine = sys.argv[3]

with open(input_file, encoding="utf-8") as f:
    sarif = json.load(f)

run = sarif["runs"][0]

driver = run["tool"]["driver"]

rules = {}

for rule in driver.get("rules", []):

    rule_id = rule["id"]

    rules[rule_id] = {
        "id": rule_id,
        "name": rule.get("name", rule_id),
        "description": rule.get("fullDescription", {}).get(
            "text",
            rule.get("shortDescription", {}).get("text", "")
        ),
        "engineId": engine,
        "cleanCodeAttribute": "TRUSTWORTHY",
        "type": "VULNERABILITY",
        "severity": map_severity(
            rule.get("defaultConfiguration", {}).get("level")
        )
    }


issues = []

for result in run.get("results", []):

    if not result.get("locations"):
        continue

    location = result["locations"][0]["physicalLocation"]

    region = location.get("region", {})

    uri = location["artifactLocation"]["uri"]

    rule_id = result["ruleId"]

    message = result["message"]["text"]

    severity = map_severity(result.get("level"))

    if rule_id not in rules:
        rules[rule_id] = {
            "id": rule_id,
            "name": rule_id,
            "description": "",
            "engineId": engine,
            "cleanCodeAttribute": "TRUSTWORTHY",
            "type": "VULNERABILITY",
            "severity": severity
        }

    issues.append(
        {
            "ruleId": rule_id,
            "primaryLocation": {

                "message": message,
                "filePath": uri,
                "textRange": {
                    "startLine": region.get("startLine", 1),
                    "endLine": region.get(
                        "endLine",
                        region.get("startLine", 1)
                    )
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

print(f"Rules  : {len(rules)}")
print(f"Issues : {len(issues)}")
print(f"Saved  : {output_file}")
