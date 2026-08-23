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

RELIABILITY: 201
SECURITY:    294
TOTAL:       495

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

Reliability:       201

Security:          294

Security Hotspots:  81


Total:             576


Final output:
```text
reports/sonarqube/merged_candidates.json
```