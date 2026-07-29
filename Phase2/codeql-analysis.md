# Running CodeQL

## Objective

Analyze the BIRD v2.17.1 source code using CodeQL by creating a CodeQL database and executing the default C/C++ security and quality query suite.

---

## Output Directory

A dedicated directory was created to store the analysis results.

```bash
mkdir -p reports/codeql
```

---

# Preparing the Project

Before creating the CodeQL database, the previous build artifacts were removed to ensure a clean build.

```bash
make clean
```

**Note:** Since the project was downloaded as a ZIP archive rather than cloned with Git, the following message appeared during the clean process:

```text
fatal: not a git repository (or any of the parent directories): .git
```
 This message is expected and does not affect the build or the analysis.

---

# Creating the CodeQL Database

Command:

```bash
codeql database create bird-db \
  --language=cpp \
  --source-root=. \
  --command="make -j$(nproc)"
```

## Result

The database was created successfully.

Database location:

```text
/home/nazanin/Projects/bird-2.17.1/bird-db
```

---

# Verifying the Query Packs

Command:

```bash
codeql resolve packs
```

The required C/C++ query pack was successfully detected.

```text
codeql/cpp-queries @1.7.0
```

---

# Running the Default Query Suite

Command:

```bash
codeql database analyze bird-db \
  codeql/cpp-queries:codeql-suites/cpp-security-and-quality.qls \
  --format=sarif-latest \
  --output=reports/codeql/codeql-results.sarif
```

## Result

The analysis completed successfully.

| Metric | Value |
|---------|------:|
| Query Suite | C/C++ Security and Quality |
| Queries Executed | 182 |
| C/C++ Files Analyzed | 172 / 211 |
| Output Format | SARIF |

Generated report:

```text
reports/codeql/codeql-results.sarif
```

---

