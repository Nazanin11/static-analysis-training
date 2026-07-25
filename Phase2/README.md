
## Phase 2 – Tool Basics (SonarQube, CodeQL, Semgrep, Cppcheck)

### Objectives
- Learn core concepts and UI/workflow for each tool.
- Understand what each tool does, what options it has, and how it fits into static analysis.
- Recognize typical noisy vs valuable findings for each.

### Activities

#### 1) Read about each tool
- SonarQube: what it scans, issue types (bugs, vulnerabilities, code smells, security hotspots), rules, quality gates.
- CodeQL: how it builds a database from code and uses queries to find patterns and vulnerabilities.
- Semgrep: pattern-based rules, common security checks, how to run and customize rules.
- Cppcheck: focus on C/C++ bugs, warnings, and typical output.

#### 2) Set up tools and BIRD on the VM
- Install SonarQube, CodeQL, Semgrep, and Cppcheck on the provided VM.
- Clone the BIRD routing daemon repository (specific version will be provided).
- Verify that BIRD builds or is at least scan-ready on the VM.

#### 3) Run each tool on BIRD

- **SonarQube**  
  - Configure a project for BIRD.  
  - Run the SonarQube scanner on the BIRD source.  
  - Explore the SonarQube UI: issues list, rule details, filters, navigation.

- **CodeQL**  
  - Create a CodeQL database for the BIRD codebase.  
  - Run the default CodeQL queries for C/C++.  
  - Inspect findings in the CodeQL CLI output and note a few example issues.

- **Semgrep**  
  - Run a standard Semgrep ruleset (e.g., `--config auto` or a recommended security config) on the BIRD source.  
  - Inspect the findings and note what kinds of patterns it reports.

- **Cppcheck**  
  - Run Cppcheck on the BIRD C/C++ files.  
  - Review warnings and errors it reports.

#### 4) Normalize other tools into SonarQube (external issues)
- Convert CodeQL, Semgrep, and Cppcheck findings into SonarQube’s external issues format (JSON).
- Import these external issues into a dedicated SonarQube project.
- Confirm in the SonarQube UI that findings from all tools appear together in the issues panel.

#### 5) Manual review and labelling
- Pick ~20 findings from the SonarQube UI (mix of tools and types).  
- For each finding:
  - Check the actual BIRD code around the line.  
  - Decide if it is a **real issue** or **noise/false positive**.  
  - Write 1–2 sentences explaining why you classified it that way.

### Reporting
- A short report (about 1 page) that:
  - Compares SonarQube, CodeQL, Semgrep, and Cppcheck on BIRD (strengths, weaknesses, typical noise).  
  - Summarizes what you learned from the ~20 manually labelled findings (patterns of real issues vs false positives).
  