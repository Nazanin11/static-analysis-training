# Static Analysis Commands – BIRD v2.17.1

## Project Setup

```bash
cd ~/Projects/bird-2.17.1
```

Create report directories:

```bash
mkdir -p reports/{cppcheck,semgrep,codeql,external}
```

---

# 1. Cppcheck

## Generate Compilation Database

```bash
bear -- make -j1
```

Check compilation database:

```bash
jq 'length' compile_commands.json
```

## Create Scoped Compilation Database

```bash
jq '
  map(
    select(
      (.file | contains("/client/")) or
      (.file | contains("/conf/")) or
      (.file | contains("/filter/")) or
      (.file | contains("/lib/")) or
      (.file | contains("/nest/")) or
      (.file | contains("/proto/")) or
      (.file | contains("/sysdep/"))
    )
  )
' compile_commands.json \
> compile_commands-analysis.json
```

Check scoped database:

```bash
jq 'length' compile_commands-analysis.json
```

Show source files:

```bash
jq -r '.[].file' compile_commands-analysis.json | sort -u
```

## Run Cppcheck

```bash
cppcheck \
  --project=compile_commands-analysis.json \
  --enable=warning,performance,portability \
  --inconclusive \
  -j1 \
  --xml \
  --xml-version=2 \
  2> reports/cppcheck/cppcheck-final-scoped.xml
```

## Count Findings

```bash
grep -c '<error ' \
  reports/cppcheck/cppcheck-final-scoped.xml
```

## Count Findings by Severity

```bash
grep '<error ' reports/cppcheck/cppcheck-final-scoped.xml \
| sed -n 's/.*severity="\([^"]*\)".*/\1/p' \
| sort \
| uniq -c
```

## Count Findings by Rule

```bash
grep '<error ' reports/cppcheck/cppcheck-final-scoped.xml \
| sed -n 's/.*id="\([^"]*\)".*/\1/p' \
| sort \
| uniq -c \
| sort -nr
```

Output:

```text
reports/cppcheck/cppcheck-final-scoped.xml
```

Final findings:

```text
113
```

---

# 2. Semgrep

## Semgrep Auto

```bash
semgrep scan \
  --config auto \
  --include='*.c' \
  --include='*.h' \
  --sarif \
  --output reports/semgrep/semgrep-auto-scoped.sarif \
  client conf filter lib nest proto sysdep
```

Output:

```text
reports/semgrep/semgrep-auto-scoped.sarif
```

## Semgrep Security Audit

```bash
semgrep scan \
  --config p/security-audit \
  --include='*.c' \
  --include='*.h' \
  --sarif \
  --output reports/semgrep/security-audit-scoped.sarif \
  client conf filter lib nest proto sysdep
```

Output:

```text
reports/semgrep/security-audit-scoped.sarif
```

## Count SARIF Results

```bash
jq '.runs[].results | length' \
  reports/semgrep/semgrep-auto-scoped.sarif
```

```bash
jq '.runs[].results | length' \
  reports/semgrep/security-audit-scoped.sarif
```

Results:

```text
Semgrep Auto       : 0 findings
Semgrep Security   : 42 findings
```

---

# 3. CodeQL

## Create Database

```bash
codeql database create bird-db-scoped \
  --language=cpp \
  --source-root=. \
  --command="make -j$(nproc)"
```

## Check Query Packs

```bash
codeql resolve packs
```

## Run Security and Quality Queries

```bash
codeql database analyze bird-db-scoped \
  codeql/cpp-queries:codeql-suites/cpp-security-and-quality.qls \
  --format=sarif-latest \
  --output=reports/codeql/codeql-results-scoped.sarif
```

## Count Results

```bash
jq '.runs[].results | length' \
  reports/codeql/codeql-results-scoped.sarif
```

## Filter Results by Source Directory

```bash
jq '
.runs[].results |= map(
  select(
    (.locations[0].physicalLocation.artifactLocation.uri | startswith("client/")) or
    (.locations[0].physicalLocation.artifactLocation.uri | startswith("conf/")) or
    (.locations[0].physicalLocation.artifactLocation.uri | startswith("filter/")) or
    (.locations[0].physicalLocation.artifactLocation.uri | startswith("lib/")) or
    (.locations[0].physicalLocation.artifactLocation.uri | startswith("nest/")) or
    (.locations[0].physicalLocation.artifactLocation.uri | startswith("proto/")) or
    (.locations[0].physicalLocation.artifactLocation.uri | startswith("sysdep/"))
  )
)
' reports/codeql/codeql-results-scoped.sarif \
> reports/codeql/codeql-results-final.sarif
```

## Count Final Results

```bash
jq '.runs[].results | length' \
  reports/codeql/codeql-results-final.sarif
```

Result:

```text
246 findings
```

## Show Findings by File

```bash
jq -r '
  .runs[].results[]
  | .locations[0].physicalLocation.artifactLocation.uri
' reports/codeql/codeql-results-final.sarif \
| sort \
| uniq -c \
| sort -nr
```

Final output:

```text
reports/codeql/codeql-results-final.sarif
```

---

# 4. Convert Results to SonarQube Format

## Semgrep Auto

```bash
python3 scripts/semgrep_to_sonar.py \
  reports/semgrep/semgrep-auto-scoped.sarif \
  reports/external/semgrep-auto-scoped.json \
  Semgrep
```

## Semgrep Security

```bash
python3 scripts/semgrep_to_sonar.py \
  reports/semgrep/security-audit-scoped.sarif \
  reports/external/semgrep-security-scoped.json \
  Semgrep
```

## CodeQL

```bash
python3 scripts/codeql_to_sonar.py \
  reports/codeql/codeql-results-final.sarif \
  reports/external/codeql-final.json
```

## Cppcheck

```bash
python3 scripts/cppcheck_to_sonar.py \
  reports/cppcheck/cppcheck-final-scoped.xml \
  reports/external/cppcheck-final-scoped.json
```

Check converted Cppcheck results:

```bash
jq '.issues | length' \
  reports/external/cppcheck-final-scoped.json
```

---

# 5. SonarQube

## Build Wrapper

The Build Wrapper output must exist before running SonarScanner:

```text
bw-output/
├── build-wrapper-dump.json
├── build-wrapper.log
└── ...
```

If a new Build Wrapper directory is required:

```bash
rm -rf bw-output
```

Run the build through Build Wrapper:

```bash
build-wrapper-linux-x86-64 \
  --out-dir bw-output \
  make clean
```

```bash
build-wrapper-linux-x86-64 \
  --out-dir bw-output \
  make -j$(nproc)
```

Verify:

```bash
ls -lh bw-output/build-wrapper-dump.json
```

---

# 6. SonarQube Project Configuration

Create:

```text
sonar-project-scoped.properties
```

Configuration:

```properties
sonar.projectKey=bird-2.17.1-scoped
sonar.projectName=bird-2.17.1-scoped
sonar.projectVersion=2.17.1

sonar.sources=.
sonar.sourceEncoding=UTF-8

sonar.host.url=http://localhost:9000
sonar.token=<PROJECT_TOKEN>

sonar.cfamily.build-wrapper-output=bw-output

sonar.exclusions=\
obj/**,\
test/**,\
tests/**,\
doc/**,\
docs/**,\
tools/**,\
distro/**,\
misc/**,\
scripts/**,\
reports/**

sonar.externalIssuesReportPaths=\
reports/external/semgrep-auto-scoped.json,\
reports/external/semgrep-security-scoped.json,\
reports/external/codeql-final.json,\
reports/external/cppcheck-final-scoped.json
```

## Run SonarScanner

```bash
sonar-scanner \
  -Dproject.settings=sonar-project-scoped.properties
```

---

# 7. Verify Imported Issues

Expected external issues:

```text
Semgrep Auto       : 0
Semgrep Security   : 42
CodeQL             : 246
Cppcheck           : 113
```

Scanner output should contain:

```text
Sensor Import external issues report
Imported 246 issues
Imported 0 issues
Imported 113 issues
Imported 42 issues
```

---

# Analysis Scope

The final analysis focuses on:

```text
client/
conf/
filter/
lib/
nest/
proto/
sysdep/
```

Excluded from SonarQube source analysis:

```text
obj/
test/
tests/
doc/
docs/
tools/
distro/
misc/
scripts/
reports/
```

---

# Output Files

```text
reports/
├── cppcheck/
│   └── cppcheck-final-scoped.xml
│
├── semgrep/
│   ├── semgrep-auto-scoped.sarif
│   └── security-audit-scoped.sarif
│
├── codeql/
│   ├── codeql-results-scoped.sarif
│   └── codeql-results-final.sarif
│
└── external/
    ├── semgrep-auto-scoped.json
    ├── semgrep-security-scoped.json
    ├── codeql-final.json
    └── cppcheck-final-scoped.json
```
