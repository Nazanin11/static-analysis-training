#!/usr/bin/env python3

import sys
import xml.etree.ElementTree as ET

ALLOWED_DIRS = (
    "client/",
    "conf/",
    "filter/",
    "lib/",
    "nest/",
    "proto/",
    "sysdep/",
)


def is_allowed(file_path):
    file_path = file_path.lstrip("./")
    return file_path.startswith(ALLOWED_DIRS)


if len(sys.argv) != 3:
    print("Usage:")
    print("python3 filter_cppcheck_scope.py input.xml output.xml")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]

tree = ET.parse(input_file)
root = tree.getroot()

errors = root.find("errors")

if errors is not None:

    for error in list(errors.findall("error")):

        locations = error.findall("location")

        # Keep the finding if at least one of its locations
        # belongs to the allowed source scope.
        keep = any(
            is_allowed(location.get("file", ""))
            for location in locations
        )

        if not keep:
            errors.remove(error)

tree.write(
    output_file,
    encoding="UTF-8",
    xml_declaration=True
)

print(f"Saved: {output_file}")
