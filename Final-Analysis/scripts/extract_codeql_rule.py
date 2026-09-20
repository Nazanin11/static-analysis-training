#!/usr/bin/env python3

import json
import re
import subprocess
import sys
from pathlib import Path


def get_metadata(text, pattern, default=None):
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1).strip() if match else default


def extract_query_metadata(query_path):
    path = Path(query_path)

    try:
        text = path.read_text(errors="ignore")
    except Exception as e:
        print(f"Warning: Could not read {path}: {e}")
        return None

    query_id = get_metadata(
        text,
        r'@id\s+([^\s*]+)',
        "unknown"
    )

    name = get_metadata(
        text,
        r'@name\s+(.+?)(?:\r?\n|\*/)',
        path.stem
    )

    description = get_metadata(
        text,
        r'@description\s+(.+?)(?:\r?\n\s*\*?\s*@|\r?\n\s*\*/)',
        None
    )

    kind = get_metadata(
        text,
        r'@kind\s+([^\s*]+)',
        None
    )

    severity = get_metadata(
        text,
        r'@problem\.severity\s+([^\s*]+)',
        None
    )

    precision = get_metadata(
        text,
        r'@precision\s+([^\s*]+)',
        None
    )

    tags = []

    tag_match = re.search(
        r'@tags\s+(.+?)(?=\r?\n\s*\*?\s*@|\r?\n\s*\*/)',
        text,
        re.DOTALL
    )

    if tag_match:
        tags = re.findall(
            r'[\w./-]+',
            tag_match.group(1)
        )

    cwes = sorted(
        set(
            re.findall(
                r'(?:cwe[-:/]?)(\d+)',
                " ".join(tags),
                re.IGNORECASE
            )
        )
    )

    return {
        "id": query_id,
        "name": name,
        "file": path.name,
        "path": str(path),
        "kind": kind,
        "severity": severity,
        "precision": precision,
        "tags": tags,
        "cwe": [f"CWE-{cwe}" for cwe in cwes],
        "description": description
    }


def main():

    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "  python3 scripts/extract_codeql_rules.py "
            "<query-suite>"
        )
        print(
            "\nExample:\n"
            "  python3 scripts/extract_codeql_rules.py "
            "codeql/cpp-queries:codeql-suites/"
            "cpp-security-and-quality.qls"
        )
        sys.exit(1)

    suite = sys.argv[1]

    print(f"Resolving Query Suite:")
    print(f"  {suite}")

    try:
        result = subprocess.run(
            [
                "codeql",
                "resolve",
                "queries",
                "--format=json",
                suite
            ],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("Error: CodeQL failed to resolve the Query Suite.")
        print(e.stderr)
        sys.exit(1)

    query_paths = json.loads(result.stdout)

    print(f"Resolved queries: {len(query_paths)}")

    queries = []

    for query_path in query_paths:
        metadata = extract_query_metadata(query_path)

        if metadata:
            queries.append(metadata)

    suite_name = Path(suite.split(":")[-1]).stem

    output_dir = Path("reports/codeql")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = (
        output_dir /
        f"{suite_name}-rules.json"
    )

    output = {
        "tool": "CodeQL",
        "version": None,
        "language": "C/C++",
        "query_pack": "codeql/cpp-queries",
        "query_suite": suite,
        "total_queries": len(queries),
        "queries": queries
    }

    try:
        version_result = subprocess.run(
            ["codeql", "--version"],
            capture_output=True,
            text=True,
            check=True
        )

        version_match = re.search(
            r"release\s+([0-9.]+)",
            version_result.stdout
        )

        if version_match:
            output["version"] = version_match.group(1)

    except Exception:
        pass

    with output_file.open("w") as f:
        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("Extraction completed successfully.")
    print(f"Total queries: {len(queries)}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
