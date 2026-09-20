#!/usr/bin/env python3

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


INPUT = Path("cppcheck/cppcheck-errorlist.xml")
OUTPUT = Path("reports/cppcheck/cppcheck-rules.json")


def main():
    if not INPUT.exists():
        print(f"Input file not found: {INPUT}")
        sys.exit(1)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    tree = ET.parse(INPUT)
    root = tree.getroot()

    cppcheck = root.find("cppcheck")
    version = cppcheck.get("version") if cppcheck is not None else None

    rules = []

    for error in root.findall("./errors/error"):
        rule = {
            "id": error.get("id"),
            "severity": error.get("severity"),
            "message": error.get("msg"),
            "verbose": error.get("verbose"),
            "cwe": error.get("cwe"),
        }

        if error.get("inconclusive") is not None:
            rule["inconclusive"] = error.get("inconclusive")

        symbols = [
            symbol.text
            for symbol in error.findall("symbol")
            if symbol.text
        ]

        if symbols:
            rule["symbols"] = symbols

        rule = {
            key: value
            for key, value in rule.items()
            if value is not None
        }

        rules.append(rule)

    # Keep only unique Check IDs
    unique_rules = {}
    for rule in rules:
        unique_rules[rule["id"]] = rule

    rules = list(unique_rules.values())

    output = {
        "tool": "Cppcheck",
        "version": version,
        "source": str(INPUT),
        "total_rules": len(rules),
        "rules": rules,
    }

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("Extraction completed successfully.")
    print(f"Cppcheck version: {version}")
    print(f"Total unique Check IDs: {len(rules)}")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
