# Rule Set Analysis

## Objective

The purpose of this analysis was to identify the rules available and used by the static analysis tools for the BIRD v2.17.1 project.

For SonarQube, the analysis distinguishes between:

1. The total number of available rules for C and C++.
2. The number of active rules in the default `Sonar way` Quality Profile.

For Semgrep, two configurations used for the BIRD analysis were examined:

1. `auto`
2. `p/security-audit`


The purpose of the CodeQL analysis was to identify the available C/C++ query suites and determine the queries selected by each suite.

The purpose of this analysis was to identify the Check IDs available in the installed Cppcheck version.

---

# 1. Total Available Rules For SonarQube

SonarQube provides a larger set of rules for each language. To determine the total number of available rules for C and C++, the SonarQube Rules API was queried.

The SonarQube server used for this analysis was:

```text
http://localhost:9000
```
## 1.1 C Rules

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

## 1.2 C++ Rules

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
## 2. Active Rules in the Sonar way Quality Profile

The total number of available rules does not represent the number of rules enabled for analysis.

SonarQube uses Quality Profiles to determine which rules are active for a language.

The default Quality Profile for both C and C++ in this SonarQube instance is:
```text
Sonar way
```
The Quality Profile API was used to identify the active rule count.

## 2.1 C Quality Profile

The Quality Profile key for C was:
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

## 2.2 C++ Quality Profile

The Quality Profile key for C++ was:
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
## 3. Saving the Rule Data as JSON

To save the complete set of available C and C++ rules as JSON files, a Python export script was created.

The script uses the SonarQube Rules API and automatically handles pagination. Therefore, the export is not limited to the first 100 or 500 rules.

The script is responsible for:

* Fetching all available C rules.
* Fetching all available C++ rules.
* Automatically requesting additional pages when required.
* Collecting all returned rules.
* Saving the complete results as JSON files.

## 3.1 Export Script

The export script is located at:

[export_sonar_rules.py](scripts/export_sonar_rules.py)

## 3.2 Output Directory

The output directory was created with:
```bash
mkdir -p rules/sonarqube
```

## 3.3 Run the Export

From the project root, run:
```bash
python3 scripts/export_sonar_rules.py
```
During execution, the script reports the current page, the number of rules received, and the total number of rules collected.

## 3.4 Generated Files

After successful execution, the following files are generated:
```text
rules/
└── sonarqube/
    ├── sonarqube-c-rules.json
    └── sonarqube-cpp-rules.json
```
These files contain the complete rule sets returned by SonarQube for the corresponding languages.

## 3.5 Active C Rules
```bash
curl -s \
  -u "$SONAR_TOKEN:" \
  "http://localhost:9000/api/rules/search?qprofile=aca11f9c-7889-4063-b2d6-f421bc3837fa&ps=500" \
  > rules/sonarqube/active/sonarqube-c-active.json
```
Verify the number of active C rules:
```bash
jq '.total' rules/sonarqube/active/sonarqube-c-active.json
```
Expected result:
```text
209
```

## 3.6 Active C++ Rules
```bash
curl -s \
  -u "$SONAR_TOKEN:" \
  "http://localhost:9000/api/rules/search?qprofile=7b1b394d-7388-4143-b3d3-42fde8740bfc&ps=500" \
  > rules/sonarqube/active/sonarqube-cpp-active.json
```
Verify the number of active C++ rules:
```bash
jq '.total' rules/sonarqube/active/sonarqube-cpp-active.json
```
Expected result:
```text
456
```
# 2. Semgrep Rule Set Analysis

## 2.1 auto Configuration

The number of Rule definitions included in the SARIF report was determined using:
```bash
jq '.runs[].tool.driver.rules | length' \
  reports/semgrep/semgrep-auto-scoped.sarif
```
Result:
```text
1074
```


C and C++ Rules in auto

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
C Rules in auto

The four C rules were:
```text
c.lang.security.insecure-use-gets-fn.insecure-use-gets-fn
c.lang.security.insecure-use-scanf-fn.insecure-use-scanf-fn
c.lang.security.insecure-use-strtok-fn.insecure-use-strtok-fn
c.lang.security.random-fd-exhaustion.random-fd-exhaustion
```


## 2.2 p/security-audit Configuration

The number of Rule definitions included in the SARIF report was determined using:
```bash
jq '.runs[].tool.driver.rules | length' \
  reports/semgrep/security-audit-scoped.sarif
```
Result:
```text
225
```

C and C++ Rules in p/security-audit

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
C Rules in p/security-audit

The nine C rules were:
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

The installed CodeQL version was:

```text
CodeQL command-line toolchain release 2.26.1 
‍
```
The C/C++ query pack used for the analysis was:

```text
codeql/cpp-queries@1.7.0
```
The available query suites were examined to determine their resolved query counts.

## 3.2 Identify Installed CodeQL Query Packs

The installed CodeQL query packs were listed using:
```text
codeql resolve packs
```
The relevant C/C++ query packs were:
```text
codeql/cpp-all@12.0.0
codeql/cpp-queries@1.7.0
```
The cpp-queries pack was used for the query suite analysis.

## 3.3 Identify Available C/C++ Query Suites

The available C/C++ query suites were identified using:
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
## 3.4 Query Suite Structure

The cpp-security-and-quality.qls suite was inspected to determine how queries are selected:
```bash
cat ~/.codeql/packages/codeql/cpp-queries/1.7.0/codeql-suites/cpp-security-and-quality.qls
```
The suite uses:
```text
security-and-quality-selectors.yml
```
to select the applicable queries.

The selector file was located using:
```bash
find ~/.codeql/packages/codeql/cpp-queries/1.7.0 \
  -name "security-and-quality-selectors.yml" \
  -print
```
The selector contains selection criteria based on:

* Query kind
* Precision
* Problem severity
* Query tags

It also excludes deprecated, experimental, model-related, and selected diagnostic queries.

## 3.5 Extract Query Metadata

To preserve the metadata of the resolved queries, a Python script was created.

The script:

* Resolves the specified CodeQL query suite.
* Collects the paths of the selected queries.
* Reads the metadata of each .ql file.
* Extracts the Query ID.
* Extracts the Query name.
* Extracts the query kind.
* Extracts severity and precision.
* Extracts tags and CWE information.
* Stores the collected information in JSON format.

The extraction script is located at:

[extract_codeql_rule.py](scripts/extract_codeql_rule.py)

The script accepts the query suite as an argument, allowing the same script to be reused for different CodeQL query suites.

For example:
```bash
python3 scripts/extract_codeql_rule.py \
  codeql/cpp-queries:codeql-suites/cpp-security-and-quality.qls
```
The resulting JSON file is:
```text
reports/codeql/cpp-security-and-quality-rules.json
```
The resulting JSON contains the query metadata, including fields such as:
```tet
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
The primary rule set used for the BIRD analysis is:
```text
cpp-security-and-quality-rules.json
```
which contains metadata for:
```text
182 queries
```
---

# 4. Cppcheck Rule Set Analysis

## 4.1 Objective

The Cppcheck version used for the BIRD analysis was:

```text
Cppcheck 2.13.0
```
## 4.2 Extract Available Check IDs

Cppcheck provides the ```--errorlist ```option to output the Check IDs and their associated metadata.

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
```text
grep -o 'id="[^"]*"' \
  cppcheck/cppcheck-errorlist.xml \
  | sort -u \
  | wc -l
```
Result:
```text
308
```
Therefore, the installed Cppcheck 2.13.0 provides 308 unique Check IDs through its --errorlist output.

## 4.3 Export Check Metadata to JSON

A Python script was created to parse the Cppcheck XML error list and store the Check metadata in JSON format.

The extraction script is located at:

[extract_cppcheck_rules.py](scripts/extract_cppcheck_rules.py)

Run the script with:
```bash
python3 scripts/extract_cppcheck_rules.py
```
The script:

* Reads the Cppcheck --errorlist XML.
* Extracts each Check ID.
* Extracts severity, message, verbose description, and CWE.
* Removes duplicate Check IDs.
* Stores the complete Check list in JSON format.

---

# C Keyword Filtering Enhancement

The `C_KEYWORDS` set in the batch-building script is used to prevent
standard C language keywords from being treated as candidate symbols
during RAG context construction.

The original keyword list was extended to include missing C99 and C11
keywords:

```python
# Missing C99/C11 keywords
"signed",
"restrict",
"_Bool",
"_Complex",
"_Imaginary",
"_Alignas",
"_Alignof",
"_Atomic",
"_Generic",
"_Noreturn",
"_Static_assert",
"_Thread_local",
```