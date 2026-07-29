# Running Semgrep

## Objective

Run Semgrep on the BIRD v2.17.1 source code using both the default automatic ruleset and a security-focused ruleset to identify potential issues.

---

## Output Directory

A dedicated directory was created to store the generated reports.

```bash
mkdir -p reports/semgrep
```

---

# Scan 1 – Automatic Ruleset

Command:

```bash
semgrep scan \
  --config auto \
  --output reports/semgrep/semgrep-auto.sarif \
  --sarif \
  .
```

### Result

The scan completed successfully.

| Metric | Value |
|---------|------:|
| Rules Executed | 347 |
| Files Scanned | 556 |
| Findings | 9 |
| Parsed Lines | ~98.7% |

Generated report:

```
reports/semgrep/semgrep-auto.sarif
```

Notes:

- The automatic ruleset provides general security and code quality coverage.
- Two files larger than 1 MB were skipped.
- Eleven files were excluded according to the `.semgrepignore` configuration.

---

# Scan 2 – Security Audit Ruleset

Command:

```bash
semgrep scan \
  --config p/security-audit \
  --output reports/semgrep/security-audit.sarif \
  --sarif \
  .
```

### Result

The scan completed successfully.

| Metric | Value |
|---------|------:|
| Rules Executed | 98 |
| Files Scanned | 556 |
| Findings | 44 |
| Parsed Lines | ~99.3% |

Generated report:

```
reports/semgrep/security-audit.sarif
```

Notes:

- The security-audit ruleset focuses specifically on security-related patterns.
- Three files larger than 1 MB were skipped.
- Eleven files were excluded according to the `.semgrepignore` configuration.

---

