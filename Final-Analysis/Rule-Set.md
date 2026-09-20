# Static Analysis Rule Set Analysis

## Objective

The purpose of this analysis was to identify and document the rule sets available and used by the static analysis tools for the BIRD v2.17.1 project.

The analysis covers four static analysis tools:

* SonarQube
* Semgrep
* CodeQL
* Cppcheck

For SonarQube, the analysis distinguishes between the total number of available C/C++ rules and the rules currently active in the default `Sonar way` Quality Profile.

For Semgrep, the rule definitions included in the two configurations used for the BIRD analysis were examined:

* `auto`
* `p/security-audit`

For CodeQL, the available C/C++ query suites were identified, and the selected queries from the `cpp-security-and-quality` suite were extracted together with their metadata.

For Cppcheck, the available Check IDs and their associated metadata were extracted from the installed Cppcheck version.

The collected rule metadata is stored as JSON and is used as the basis for subsequent rule filtering and analysis.

---

# 1. SonarQube Rule Set Analysis

## 1.1 Total Available C/C++ Rules

SonarQube provides a set of rules for each supported language. To determine the total number of available rules for C and C++, the SonarQube Rules API was queried.

The SonarQube server used for this analysis was:

```text
http://localhost:9000
```

### 1.1.1 C Rules

Command:

```bash
curl -s \
  -u "$SONAR_TOKEN:" \
  "http://localhost:9000/api/rules/search?languages=c&ps=100" \
  | jq '.total'
```

Result:

```text
Total available C rules = 420
```

### 1.1.2 C++ Rules

Command:

```bash
curl -s \
  -u "$SONAR_TOKEN:" \
  "http://localhost:9000/api/rules/search?languages=cpp&ps=100" \
  | jq '.total'
```

Result:

```text
Total available C++ rules = 806
```

These values represent the total number of rules available for the respective languages in the SonarQube instance. They do not indicate which rules are currently active for the BIRD project.

---

## 1.2 Active Rules in the `Sonar way` Quality Profile

SonarQube uses Quality Profiles to determine which rules are active for a language.

The default Quality Profile for both C and C++ in this SonarQube instance is:

```text
Sonar way
```

The Quality Profile API was used to determine the number of active rules.

### 1.2.1 C Quality Profile

The Quality Profile key for C is:

```text
aca11f9c-7889-4063-b2d6-f421bc3837fa
```

Command:

```bash
curl -s \
  -u "$SONAR_TOKEN:" \
  "http://localhost:9000/api/qualityprofiles/show?key=aca11f9c-7889-4063-b2d6-f421bc3837fa" \
  | jq '.profile | {
      key,
      name,
      language,
      languageName,
      isDefault,
      activeRuleCount
    }'
```

Result:

```text
{
  "key": "aca11f9c-7889-4063-b2d6-f421bc3837fa",
  "name": "Sonar way",
  "language": "c",
  "languageName": "C",
  "isDefault": true,
  "activeRuleCount": 209
}
```

Therefore:

```text
Active C rules in Sonar way = 209
```

### 1.2.2 C++ Quality Profile

The Quality Profile key for C++ is:

```text
7b1b394d-7388-4143-b3d3-42fde8740bfc
```

Command:

```bash
curl -s \
  -u "$SONAR_TOKEN:" \
  "http://localhost:9000/api/qualityprofiles/show?key=7b1b394d-7388-4143-b3d3-42fde8740bfc" \
  | jq '.profile | {
      key,
      name,
      language,
      languageName,
      isDefault,
      activeRuleCount
    }'
```

Result:

```text
{
  "key": "7b1b394d-7388-4143-b3d3-42fde8740bfc",
  "name": "Sonar way",
  "language": "cpp",
  "languageName": "C++",
  "isDefault": true,
  "activeRuleCount": 456
}
```

Therefore:

```text
Active C++ rules in Sonar way = 456
```

---

## 1.3 Export SonarQube Rule Metadata to JSON

To preserve the complete set of available C and C++ rules, a Python export script was created.

The script uses the SonarQube Rules API and handles pagination automatically. Therefore, the export is not limited to the first API page.

The script is responsible for:

* Fetching all available C rules.
* Fetching all available C++ rules.
* Handling API pagination.
* Collecting all returned rules.
* Saving the rule metadata as JSON files.

### 1.3.1 Export Script

The export script is located at:

[export_sonar_rules.py](scripts/export_sonar_rules.py)

### 1.3.2 Create the Output Directory

```bash
mkdir -p rules/sonarqube
```

### 1.3.3 Run the Export

From the project root:

```bash
python3 scripts/export_sonar_rules.py
```

During execution, the script reports the current page, the number of rules received, and the total number of rules collected.

### 1.3.4 Generated Files

After successful execution:

```text
rules/
└── sonarqube/
    ├── sonarqube-c-rules.json
    └── sonarqube-cpp-rules.json
```

These files contain the complete rule metadata returned by SonarQube for the corresponding languages.

---

## 1.4 Export Active C Rules

The active C rules from the `Sonar way` Quality Profile were exported using the Quality Profile key.

First, create the output directory:

```bash
mkdir -p rules/sonarqube/active
```

Export the active C rules:

```bash
curl -s \
  -u "$SONAR_TOKEN:" \
  "http://localhost:9000/api/rules/search?qprofile=aca11f9c-7889-4063-b2d6-f421bc3837fa&ps=500" \
  > rules/sonarqube/active/sonarqube-c-active.json
```

Verify the number of active rules:

```bash
jq '.total' rules/sonarqube/active/sonarqube-c-active.json
```

Expected result:

```text
209
```

---

## 1.5 Export Active C++ Rules

The active C++ rules from the `Sonar way` Quality Profile were exported using the corresponding Quality Profile key.

Command:

```bash
curl -s \
  -u "$SONAR_TOKEN:" \
  "http://localhost:9000/api/rules/search?qprofile=7b1b394d-7388-4143-b3d3-42fde8740bfc&ps=500" \
  > rules/sonarqube/active/sonarqube-cpp-active.json
```

Verify the number of active rules:

```bash
jq '.total' rules/sonarqube/active/sonarqube-cpp-active.json
```

Expected result:

```text
456
```

---

# 2. Semgrep Rule Set Analysis

Two Semgrep configurations were used during the BIRD analysis:

* `auto`
* `p/security-audit`

The rule definitions included in their SARIF reports were examined to identify the C and C++ rules relevant to the project.

---

## 2.1 `auto` Configuration

The total number of rule definitions included in the `auto` SARIF report was determined using:

```bash
jq '[.runs[].tool.driver.rules | length] | add' \
  reports/semgrep/semgrep-auto-scoped.sarif
```

Result:

```text
1074
```

### 2.1.1 C/C++ Rules in `auto`

The Rule IDs were filtered to identify C and C++ rules:

```bash
jq -r '
  .runs[].tool.driver.rules[]
  | select(
      (.id | startswith("c."))
      or
      (.id | startswith("cpp."))
    )
  | .id
' reports/semgrep/semgrep-auto-scoped.sarif \
| sort -u \
| tee /tmp/semgrep-c-cpp-auto-rules.txt
```

Count:

```bash
wc -l /tmp/semgrep-c-cpp-auto-rules.txt
```

Result:

```text
4
```

C rules:

```bash
grep '^c\.' /tmp/semgrep-c-cpp-auto-rules.txt | wc -l
```

Result:

```text
4
```

C++ rules:

```bash
grep '^cpp\.' /tmp/semgrep-c-cpp-auto-rules.txt | wc -l
```

Result:

```text
0
```

The four C rules identified in the `auto` configuration were:

```text
c.lang.security.insecure-use-gets-fn.insecure-use-gets-fn
c.lang.security.insecure-use-scanf-fn.insecure-use-scanf-fn
c.lang.security.insecure-use-strtok-fn.insecure-use-strtok-fn
c.lang.security.random-fd-exhaustion.random-fd-exhaustion
```

---

## 2.2 `p/security-audit` Configuration

The total number of rule definitions included in the `p/security-audit` SARIF report was determined using:

```bash
jq '[.runs[].tool.driver.rules | length] | add' \
  reports/semgrep/security-audit-scoped.sarif
```

Result:

```text
225
```

### 2.2.1 C/C++ Rules in `p/security-audit`

The C and C++ Rule IDs were extracted using:

```bash
jq -r '
  .runs[].tool.driver.rules[]
  | select(
      (.id | startswith("c."))
      or
      (.id | startswith("cpp."))
    )
  | .id
' reports/semgrep/security-audit-scoped.sarif \
| sort -u \
| tee /tmp/semgrep-c-cpp-security-rules.txt
```

Count:

```bash
wc -l /tmp/semgrep-c-cpp-security-rules.txt
```

Result:

```text
9
```

C rules:

```bash
grep '^c\.' /tmp/semgrep-c-cpp-security-rules.txt | wc -l
```

Result:

```text
9
```

C++ rules:

```bash
grep '^cpp\.' /tmp/semgrep-c-cpp-security-rules.txt | wc -l
```

Result:

```text
0
```

The nine C rules identified in the `p/security-audit` configuration were:

```text
c.lang.security.double-free.double-free
c.lang.security.insecure-use-gets-fn.insecure-use-gets-fn
c.lang.security.insecure-use-printf-fn.insecure-use-printf-fn
c.lang.security.insecure-use-scanf-fn.insecure-use-scanf-fn
c.lang.security.insecure-use-strcat-fn.insecure-use-strcat-fn
c.lang.security.insecure-use-string-copy-fn.insecure-use-string-copy-fn
c.lang.security.insecure-use-strtok-fn.insecure-use-strtok-fn
c.lang.security.random-fd-exhaustion.random-fd-exhaustion
c.lang.security.use-after-free.use-after-free
```

---

# 3. CodeQL Rule Set Analysis

## 3.1 Objective

The CodeQL analysis was performed to identify the available C/C++ query suites and determine the queries selected by the security-focused query suite used for the BIRD analysis.

The installed CodeQL version was:

```text
CodeQL command-line toolchain release 2.26.1
```

The C/C++ query pack used for the analysis was:

```text
codeql/cpp-queries@1.7.0
```

---

## 3.2 Identify Installed CodeQL Query Packs

The installed CodeQL query packs were listed using:

```bash
codeql resolve packs
```

The relevant C/C++ query packs were:

```text
codeql/cpp-all@12.0.0
codeql/cpp-queries@1.7.0
```

The `codeql/cpp-queries@1.7.0` pack was used for the query suite analysis.

---

## 3.3 Identify Available C/C++ Query Suites

The available query suites in the installed C/C++ query pack were identified using:

```bash
find ~/.codeql/packages/codeql/cpp-queries/1.7.0 \
  -type f \
  -name "*.qls"
```

The following query suites were available:

```text
cpp-lgtm.qls
cpp-code-quality-extended.qls
cpp-security-experimental.qls
cpp-code-scanning.qls
cpp-code-quality.qls
cpp-lgtm-full.qls
cpp-security-extended.qls
cpp-security-and-quality.qls
```

---

## 3.4 Inspect the Query Suite Structure

The `cpp-security-and-quality.qls` suite was inspected to determine how its queries are selected:

```bash
cat ~/.codeql/packages/codeql/cpp-queries/1.7.0/codeql-suites/cpp-security-and-quality.qls
```

The suite uses:

```text
security-and-quality-selectors.yml
```

to define the query-selection criteria.

The selector file was located using:

```bash
find ~/.codeql/packages/codeql/cpp-queries/1.7.0 \
  -name "security-and-quality-selectors.yml" \
  -print
```

The selector criteria include properties such as:

* Query kind
* Precision
* Problem severity
* Query tags

The suite also excludes deprecated, experimental, model-related, and selected diagnostic queries according to its selector configuration.

---

## 3.5 Extract CodeQL Query Metadata

To preserve the metadata of the resolved CodeQL queries, a Python extraction script was created.

The script:

* Resolves the specified CodeQL query suite.
* Collects the paths of the selected queries.
* Reads the metadata of each `.ql` file.
* Extracts the query ID.
* Extracts the query name.
* Extracts the query kind.
* Extracts severity and precision.
* Extracts tags and CWE information.
* Stores the collected metadata in JSON format.

The extraction script is located at:

[extract_codeql_rule.py](scripts/extract_codeql_rule.py)

The script accepts the query suite as an argument, allowing the same script to be reused with different CodeQL query suites.

For example:

```bash
python3 scripts/extract_codeql_rule.py \
  codeql/cpp-queries:codeql-suites/cpp-security-and-quality.qls
```

The resulting JSON file is:

```text
reports/codeql/cpp-security-and-quality-rules.json
```

The JSON file contains query metadata including:

```text
id
name
file
path
kind
severity
precision
tags
cwe
description
```

The primary CodeQL rule set used for the BIRD analysis is:

```text
cpp-security-and-quality-rules.json
```

It contains metadata for:

```text
182 queries
```

---

# 4. Cppcheck Rule Set Analysis

## 4.1 Objective

The Cppcheck analysis was performed to identify the Check IDs available in the installed Cppcheck version and preserve their associated metadata.

The Cppcheck version used for the BIRD analysis was:

```text
Cppcheck 2.13.0
```

---

## 4.2 Extract Available Check IDs

Cppcheck provides the `--errorlist` option to output the available Check IDs together with their associated metadata.

The complete Cppcheck error list was generated using:

```bash
cppcheck --errorlist > cppcheck/cppcheck-errorlist.xml
```

The generated XML contains information such as:

* Check ID
* Severity
* Message
* Verbose description
* CWE
* Additional metadata

The number of unique Check IDs was verified using:

```bash
grep -o 'id="[^"]*"' \
  cppcheck/cppcheck-errorlist.xml \
  | sort -u \
  | wc -l
```

Result:

```text
308
```

Therefore, the installed Cppcheck 2.13.0 provides:

```text
308 unique Check IDs
```

through its `--errorlist` output.

---

## 4.3 Export Cppcheck Check Metadata to JSON

A Python script was created to parse the Cppcheck XML error list and store the Check metadata in JSON format.

The extraction script is located at:

[extract_cppcheck_rules.py](scripts/extract_cppcheck_rules.py)

Run the script with:

```bash
python3 scripts/extract_cppcheck_rules.py
```

The script:

* Reads the Cppcheck `--errorlist` XML.
* Extracts each Check ID.
* Extracts severity, message, verbose description, and CWE information.
* Removes duplicate Check IDs.
* Stores the complete Check metadata in JSON format.

The resulting rule metadata file is:

```text
cppcheck/cppcheck-rules.json
```

This file provides the Cppcheck rule metadata used by subsequent analysis stages.

---

# 5. Rule Set Analysis Summary

The rule-set analysis identified the following rule/query sets used as inputs for the subsequent stages:

| Tool      | Configuration / Rule Set                  | Result |
| --------- | ----------------------------------------- | -----: |
| SonarQube | Available C rules                         |    420 |
| SonarQube | Available C++ rules                       |    806 |
| SonarQube | Active C rules (`Sonar way`)              |    209 |
| SonarQube | Active C++ rules (`Sonar way`)            |    456 |
| Semgrep   | `auto` total rule definitions             |   1074 |
| Semgrep   | C/C++ rules in `auto`                     |      4 |
| Semgrep   | `p/security-audit` total rule definitions |    225 |
| Semgrep   | C/C++ rules in `p/security-audit`         |      9 |
| CodeQL    | `cpp-security-and-quality` queries        |    182 |
| Cppcheck  | Available Check IDs                       |    308 |


---
