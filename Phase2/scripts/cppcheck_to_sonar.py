
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


def map_issue_type(severity):
    """
    Map Cppcheck severity to SonarQube external issue type.

    error/warning       -> BUG
    style/performance/
    portability         -> CODE_SMELL
    information/debug   -> CODE_SMELL
    """

    severity = (severity or "").lower()

    mapping = {
        "error": "BUG",
        "warning": "BUG",
        "style": "CODE_SMELL",
        "performance": "CODE_SMELL",
        "portability": "CODE_SMELL",
        "information": "CODE_SMELL",
        "debug": "CODE_SMELL"
    }

    return mapping.get(severity, "CODE_SMELL")


if len(sys.argv) != 3:
    print("Usage:")
    print("python3 cppcheck_to_sonar.py input.xml output.json")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


# -------------------------------------------------------------------
# Parse Cppcheck XML
# -------------------------------------------------------------------

tree = ET.parse(input_file)
root = tree.getroot()

rules = {}
issues = []

errors = root.find("errors")


if errors is not None:

    for error in errors.findall("error"):

        rule_id = error.get("id", "cppcheck")
        severity_raw = error.get("severity", "")

        severity = map_severity(severity_raw)
        issue_type = map_issue_type(severity_raw)

        description = (
            error.get("verbose")
            or error.get("msg")
            or ""
        )

        # -----------------------------------------------------------
        # Create rule only once
        # -----------------------------------------------------------

        if rule_id not in rules:

            rules[rule_id] = {
                "id": rule_id,
                "name": error.get("msg", rule_id),
                "description": description,
                "engineId": "Cppcheck",
                "cleanCodeAttribute": "TRUSTWORTHY",
                "type": issue_type,
                "severity": severity
            }

        # -----------------------------------------------------------
        # Collect valid locations
        # -----------------------------------------------------------

        valid_locations = []

        for loc in error.findall("location"):

            file_path = loc.get("file")

            if not file_path:
                continue

            if not os.path.isfile(file_path):
                continue

            try:
                line = int(loc.get("line", "1"))
            except ValueError:
                line = 1

            line = clamp_line(file_path, line)

            valid_locations.append(
                {
                    "filePath": file_path,
                    "line": line
                }
            )

        # -----------------------------------------------------------
        # One Cppcheck finding = one Sonar issue
        # -----------------------------------------------------------

        if not valid_locations:
            continue

        primary = valid_locations[0]

        issue = {
            "ruleId": rule_id,
            "primaryLocation": {
                "message": description,
                "filePath": primary["filePath"],
                "textRange": {
                    "startLine": primary["line"],
                    "endLine": primary["line"]
                }
            }
        }

        # -----------------------------------------------------------
        # Preserve additional Cppcheck locations as secondary
        # locations instead of creating additional Sonar issues.
        # -----------------------------------------------------------

        if len(valid_locations) > 1:

            secondary_locations = []

            for location in valid_locations[1:]:

                secondary_locations.append(
                    {
                        "message": description,
                        "filePath": location["filePath"],
                        "textRange": {
                            "startLine": location["line"],
                            "endLine": location["line"]
                        }
                    }
                )

            issue["secondaryLocations"] = secondary_locations

        issues.append(issue)


# -------------------------------------------------------------------
# Create SonarQube External Issues Report
# -------------------------------------------------------------------

sonar = {
    "rules": list(rules.values()),
    "issues": issues
}


output_dir = os.path.dirname(output_file)

if output_dir:
    os.makedirs(output_dir, exist_ok=True)


with open(output_file, "w", encoding="utf-8") as f:
    json.dump(sonar, f, indent=2)


print(f"Rules : {len(rules)}")
print(f"Issues: {len(issues)}")
print(f"Saved : {output_file}")
