#!/usr/bin/env python3

import json
import os
import sys
import xml.etree.ElementTree as ET

def clamp_line(file_path, line):
    try:
        if not os.path.isfile(file_path):
            return 1

        with open(file_path, "rb") as f:
            max_line = sum(1 for _ in f)

        if max_line == 0:
            return 1

        return max(1, min(line, max_line))

    except Exception:
        return 1
        
def map_severity(severity):
    severity = (severity or "").lower()

    mapping = {
        "error": "CRITICAL",
        "warning": "MAJOR",
        "style": "MINOR",
        "performance": "MINOR",
        "portability": "MINOR",
        "information": "INFO",
        "debug": "INFO"
    }

    return mapping.get(severity, "MAJOR")

if len(sys.argv) != 3:
    print("Usage:")
    print("python3 cppcheck_to_sonar.py input.xml output.json")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]

tree = ET.parse(input_file)
root = tree.getroot()

rules = {}
issues = []

errors = root.find("errors")

if errors is not None:

    for error in errors.findall("error"):

        rule_id = error.get("id", "cppcheck")
        severity = map_severity(error.get("severity"))

        description = error.get("verbose") or error.get("msg") or ""

        if rule_id not in rules:

            rules[rule_id] = {
                "id": rule_id,
                "name": error.get("msg", rule_id),
                "description": description,
                "engineId": "Cppcheck",
                "cleanCodeAttribute": "TRUSTWORTHY",
                "type": "CODE_SMELL",
                "severity": severity
            }

        for loc in error.findall("location"):

            file_path = loc.get("file")

            if not file_path or not os.path.isfile(file_path):
                continue

            try:
                line = int(loc.get("line", "1"))
            except ValueError:
                line = 1

            line = clamp_line(file_path, line)

            issues.append(
                {
                    "ruleId": rule_id,
                    "primaryLocation": {
                        "message": description,
                        "filePath": file_path,
                        "textRange": {
                            "startLine": line,
                            "endLine": line
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
