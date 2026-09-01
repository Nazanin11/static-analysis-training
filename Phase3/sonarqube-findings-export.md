# SonarQube Findings Export and Merge

## Objective

Extract all SonarQube findings related to **Reliability**, **Security**, and **Security Hotspots** for the BIRD v2.17.1 project and merge them into a single JSON file.

---

## 1. Export Security and Reliability Findings

Since the total number of SonarQube issues is greater than 500, all issues are retrieved page by page and then filtered.

Script:


[export_sonar_security_reliability.py](scripts/export_sonar_security_reliability.py)

The script:

* Retrieves all SonarQube issues using the /api/issues/search API.
* Handles pagination with ps=500.
* Keeps findings with RELIABILITY or SECURITY software quality.
* Removes MAINTAINABILITY findings.

Generates the following output:
```text
reports/sonarqube/sonarqube-security-reliability.json
```

Run:
```bash
python3 scripts/export_sonar_security_reliability.py
```
Result:

RELIABILITY: 196
SECURITY:    130
TOTAL:       326

## 2. Export Security Hotspots

Security Hotspots are retrieved separately using the SonarQube Hotspots API.

Command:
```bash
curl -s -u "$SONAR_TOKEN:" \
"http://localhost:9000/api/hotspots/search?projectKey=bird-2.17.1-scoped&ps=500" \
-o reports/sonarqube/sonarqube-hotspots.json
```
Verify the number of hotspots:
```bash
jq '.paging.total' reports/sonarqube/sonarqube-hotspots.json
```
Result:
```text
Security Hotspots: 81
```
## 3. Merge SonarQube Findings

The filtered Security/Reliability findings and Security Hotspots are merged into one JSON file.

Script:

[merge_sonarqube_findings.py](scripts/merge_sonarqube_findings.py)

The script reads:
```text
reports/sonarqube/sonarqube-security-reliability.json
reports/sonarqube/sonarqube-hotspots.json
```
and generates:
```text
reports/sonarqube/merged_candidates.json
```
Run:
```bash
python3 scripts/merge_sonarqube_findings.py
```

## 4. Final Result

The final consolidated file contains:

Reliability:       196

Security:          130

Security Hotspots:  81


Total:             407


Final output:
```text
reports/sonarqube/merged_candidates.json
```
---

## 5. Add CWE Metadata to CodeQL Findings

The CodeQL findings contained in `merged_candidates.json` were enriched with the CWE information obtained from the CodeQL query metadata.


The enrichment was then performed using the following script:


[add_codeql_cwe.py](scripts/add_codeql_cwe.py)



The enrichment script was executed using:

```bash
python3 scripts/add_codeql_cwe.py
```

The script reports:

```text
Total findings:          407
CodeQL findings:         82
CodeQL with CWE:         82
CodeQL without CWE:      0
```

The enriched output was generated as:

```text
reports/sonarqube/merged_candidates_with_cwe.json
```

The resulting CodeQL findings now contain a `cwe` field. For example:

```json
{
  "rule": "external_CodeQL:cpp/unbounded-write",
  "cwe": [
    "CWE-120",
    "CWE-787",
    "CWE-805"
  ]
}
```

Therefore, CWE metadata is added to the CodeQL findings while preserving the original finding information. This metadata can subsequently be passed to the LLM triage stage as additional contextual information.

---

## 6. Add CWE Metadata to Cppcheck Findings**

The Cppcheck findings contained in `merged_candidates.json` were enriched with CWE information obtained from the Cppcheck rule metadata.

The Cppcheck rule metadata was stored in:

```text
cppcheck/cppcheck-rules.json
```

The rule metadata was verified using:

```bash
python3 - <<'PY'
import json

FILE = "cppcheck/cppcheck-rules.json"

with open(FILE, encoding="utf-8") as f:
    data = json.load(f)

rules = data["rules"]

with_cwe = [r for r in rules if r.get("cwe")]

print("Total rules:", len(rules))
print("Rules with CWE:", len(with_cwe))
print("Rules without CWE:", len(rules) - len(with_cwe))
PY
```

The result was:

```text
Total rules: 308
Rules with CWE: 277
Rules without CWE: 31
```

The enrichment was then performed using the following script:


[add_cppcheck_cwe.py](scripts/add_cppcheck_cwe.py)


The script was executed using:

```bash
python3 scripts/add_cppcheck_cwe.py
```

The script reports:

```text
Total findings:          407
Cppcheck findings:        95
Cppcheck with CWE:        28
Cppcheck without CWE:     67
Matched rules:             28
```

The enriched output was generated as:

```text
reports/sonarqube/merged_candidates_with_cwe.json
```

The resulting Cppcheck findings now contain a `cwe` field when a corresponding CWE mapping is available. For example:

```json
{
  "rule": "external_Cppcheck:nullPointerArithmeticRedundantCheck",
  "cwe": [
    "CWE-682"
  ]
}
```

For findings whose Cppcheck rules do not have a CWE mapping, the field remains empty:

```json
{
  "rule": "external_Cppcheck:allocaCalled",
  "cwe": []
}
```

Therefore, CWE metadata is added to the Cppcheck findings where a valid mapping exists, while all original findings are preserved. Findings without CWE mappings are not removed and remain available for the subsequent LLM triage stage.

---

## 7. Add CWE Metadata to SonarQube Findings

The SonarQube findings in `merged_candidates.json` were enriched with CWE metadata obtained from the SonarQube rule descriptions through the SonarQube API.

The enrichment script is:


[add_sonar_cwe.py](scripts/add_sonar_cwe.py)


The script identifies the unique SonarQube rules present in the findings and retrieves their rule metadata using:

```text
/api/rules/show?key=<ruleKey>
```

CWE identifiers are then extracted from the rule `descriptionSections` and added to the corresponding findings.

The script was executed using:

```bash
python3 scripts/add_sonar_cwe.py
```

The script reported:

```text
Total findings:          407
SonarQube findings:      188
Unique Sonar rules:      18

SonarQube with CWE:      139
SonarQube without CWE:   49

Sonar rules:             18
Rules with CWE:          9
Rules without CWE:       6
```

The enriched output was written to:

```text
reports/sonarqube/merged_candidates_with_cwe.json
```

## Security Hotspots

Security Hotspots were already included in the merged findings during the previous merge stage. Their presence and CWE enrichment were verified separately.

A total of **81 Security Hotspots** were found in the final file, and all 81 contained CWE metadata:

```text
Findings with ruleKey: 81
With CWE:             81
Without CWE:           0
```

The Security Hotspots were associated with three SonarQube rules:

```text
c:S5816: 13
c:S5813: 41
c:S5801: 27
```

All three rules were mapped to `CWE-120`.

Therefore, both regular SonarQube findings and Security Hotspots are retained in the consolidated file, with CWE metadata added where available.

---

## 8. Add CWE Metadata to Semgrep Findings

The Semgrep findings contained in `merged_candidates_with_cwe.json` were enriched with CWE information obtained from the Semgrep rule metadata file.
The enrichment was then performed using the following script:


[add_semgrep_cwe.py](scripts/add_semgrep_cwe.py)



The enrichment was performed using the following script:

```bash
python3 scripts/add_semgrep_cwe.py
```

The script identifies Semgrep findings using the `externalRuleEngine` field and extracts the original Semgrep rule ID from the finding's `rule` field.

For example, a Semgrep finding contains a rule value such as:

```text
external_Semgrep:c.lang.security.insecure-use-string-copy-fn.insecure-use-string-copy-fn
```

The script extracts the original Semgrep rule ID:

```text
insecure-use-string-copy-fn
```

This ID is then matched against the `id` field in the Semgrep rule metadata. The corresponding CWE metadata is retrieved and added to the finding.

For example:

```json
{
  "id": "insecure-use-string-copy-fn",
  "cwe": [
    "CWE-676: Use of Potentially Dangerous Function"
  ]
}
```

is converted to the following CWE metadata in the finding:

```json
{
  "cwe": [
    "CWE-676"
  ]
}
```

The enrichment script produced the following results:

```text
============================================================
Semgrep CWE Enrichment
============================================================
Total findings:          407
Semgrep findings:        42
Unique Semgrep rules:    1

Resolving Semgrep rules:
------------------------------------------------------------
insecure-use-string-copy-fn                   -> CWE-676

============================================================
Enrichment completed
============================================================
Total findings:          407
Semgrep findings:        42
Semgrep with CWE:        42
Semgrep without CWE:     0

Semgrep rules:           1
Rules with CWE:          1
Rules without CWE:       0
```

Therefore, all 42 Semgrep findings currently present in the merged findings were successfully enriched with CWE metadata, and no Semgrep finding remained without a CWE.

The enriched findings were written to:

```text
reports/sonarqube/merged_candidates_with_cwe.json
```

The `cwe` metadata can subsequently be used as additional security context during the LLM triage stage.
