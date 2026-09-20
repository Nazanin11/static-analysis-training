# BIRD v2.17.1 – Static Analysis End-to-End Guide

**Project:** BIRD Routing Daemon

**Version:** v2.17.1

**Purpose:** Reproduce the complete static analysis workflow on a new environment.

---

# 1. Environment Setup

## 1.1 Operating System

The analysis environment was based on:

```text
Ubuntu 24.04.4 LTS
Architecture: x86_64
```

Verify the operating system:

```bash
lsb_release -a
```

Verify the system architecture:

```bash
uname -m
```

---

## 1.2 Update Package Lists

Before installing the required tools, update the package index:

```bash
sudo apt update
```

Upgrade installed packages if required:

```bash
sudo apt upgrade -y
```

---

# 2. Required System Packages

The following packages were installed as part of the analysis environment.

## 2.1 Basic Development and Utility Tools

```bash
sudo apt install -y \
    git \
    curl \
    wget \
    unzip \
    zip \
    build-essential
```

These packages provide:

* `git` – source-code management
* `curl` – downloading resources and testing HTTP/HTTPS connectivity
* `wget` – downloading source archives
* `unzip` – extracting ZIP archives
* `zip` – creating ZIP archives
* `build-essential` – GCC, Make and required compilation tools

---

## 2.2 Python Environment

Python and the required package-management tools were installed with:

```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    pipx
```

Verify Python:

```bash
python3 --version
```

Verify pip:

```bash
pip3 --version
```

Verify pipx:

```bash
pipx --version
```

---

## 2.3 Java

Java was required for SonarQube and SonarScanner.

Install OpenJDK:

```bash
sudo apt install -y openjdk-17-jdk
```

Verify Java:

```bash
java -version
```

Verify the compiler:

```bash
javac -version
```

---

## 2.4 Verify Git

Check the installed Git version:

```bash
git --version
```

Example:

```text
git version 2.43.0
```

---

# 3. Static Analysis Tools Installation

## 3.1 Semgrep

Semgrep was installed using `pipx`.

```bash
pipx install semgrep
```

Verify the installation:

```bash
semgrep --version
```

Installed version:

```text
Semgrep 1.170.0
```

### Installation Issue

A direct `pip` installation was initially attempted but failed because Ubuntu 24.04 uses an externally managed Python environment.

The following error was encountered:

```text
error: externally-managed-environment
```

### Solution

Semgrep was installed using `pipx` instead:

```bash
pipx install semgrep
```

This installs Semgrep in an isolated Python environment without modifying the system Python environment.

---

## 3.2 Cppcheck

Cppcheck was installed from the Ubuntu package repository:

```bash
sudo apt install -y cppcheck
```

Verify the installation:

```bash
cppcheck --version
```

Installed version:

```text
Cppcheck 2.13.0
```

---

## 3.3 SonarQube and SonarScanner

SonarQube was installed using the native installation method on Ubuntu 24.04.

The installation included:

* SonarQube server
* PostgreSQL database
* Java 21
* SonarScanner CLI
* Systemd service
* Required system resource limits

---

## 3.3.1 Download and Extract SonarQube

Download the SonarQube package and extract it:

```bash
unrar x SonarQube_Data_Center_Edition_2026.3.0.123014_MultiOS_Downloadly.ir.rar
cd "SonarQube Data Center Edition 2026.3.0.123014 MultiOS"
unzip sonarqube-datacenter-2026.3.0.123014_Downloadly.ir.zip
```

Enter the extracted SonarQube directory:

```bash
cd sonarqube-2026.3.0.123014/
```

---

## 3.3.2 PostgreSQL Installation

Install PostgreSQL:

```bash
sudo apt update
sudo apt install -y postgresql-common postgresql
```

Enable and start PostgreSQL:

```bash
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

Open the PostgreSQL shell:

```bash
sudo -u postgres psql
```

Create the SonarQube database user and database:

```sql
CREATE ROLE sonaruser WITH LOGIN ENCRYPTED PASSWORD 'sonarmasteruser';
CREATE DATABASE sonarqube;
GRANT ALL PRIVILEGES ON DATABASE sonarqube TO sonaruser;
\c sonarqube
GRANT ALL PRIVILEGES ON SCHEMA public TO sonaruser;
\q
```

---

## 3.3.3 Java 21 Installation

SonarQube 2026.3 requires Java 21.

Install OpenJDK 21:

```bash
sudo apt install -y openjdk-21-jdk
```

Verify the installation:

```bash
java -version
```

---

## 3.3.4 SonarQube Core Setup

Move the SonarQube installation to `/opt`:

```bash
mv sonarqube-2026.3.0.123014/ sonarqube
sudo mv sonarqube/ /opt/sonarqube
```

Create a dedicated system user:

```bash
sudo adduser --system --no-create-home --group --disabled-login sonarqube
```

> Ownership is intentionally not changed at this stage. It is applied after all SonarQube configuration files have been modified.

---

## 3.3.5 SonarScanner CLI Installation

Install SonarScanner separately from the SonarQube server:

```bash
cd /opt/sonarqube
sudo wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-8.1.0.6389.zip
sudo unzip sonar-scanner-cli-8.1.0.6389.zip
sudo mv sonar-scanner-8.1.0.6389/ /opt/sonar-scanner
```

Configure the scanner:

```bash
sudo nano /opt/sonar-scanner/conf/sonar-scanner.properties
```

Add:

```properties
sonar.host.url=127.0.0.1
```

Make the scanner executable:

```bash
sudo chmod +x /opt/sonar-scanner/bin/sonar-scanner
```

Create a global command:

```bash
sudo ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner
```

Verify the installation:

```bash
sonar-scanner -v
```

Expected version:

```text
SonarScanner CLI 8.1.0.6389
```

---

## 3.3.6 SonarQube Configuration

Edit the SonarQube configuration:

```bash
sudo nano /opt/sonarqube/conf/sonar.properties
```

Configure the PostgreSQL connection:

```properties
sonar.jdbc.username=sonaruser
sonar.jdbc.password=your_password
sonar.jdbc.url=jdbc:postgresql://localhost:5432/sonarqube
```

Configure the SonarQube web server:

```properties
sonar.web.javaAdditionalOpts=-server
sonar.web.host=0.0.0.0
sonar.web.port=9000
```

After all modifications are complete, assign ownership to the dedicated SonarQube user:

```bash
sudo chown -R sonarqube:sonarqube /opt/sonarqube
```

---

## 3.3.7 System Resource Limits

SonarQube uses Elasticsearch internally and requires increased system limits.

Edit the system configuration:

```bash
sudo nano /etc/sysctl.conf
```

Add:

```text
vm.max_map_count=524288
fs.file-max=131072
```

Apply the changes:

```bash
sudo sysctl -p
```

Configure limits for the SonarQube user:

```bash
sudo nano /etc/security/limits.d/99-sonarqube.conf
```

Add:

```text
sonarqube   -   nofile   131072
sonarqube   -   nproc    8192
```

---

## 3.3.8 Systemd Service

Create a systemd service:

```bash
sudo nano /etc/systemd/system/sonarqube.service
```

Add:

```ini
[Unit]
Description=SonarQube service
After=syslog.target network.target

[Service]
Type=forking

ExecStart=/opt/sonarqube/bin/linux-x86-64/sonar.sh start
ExecStop=/opt/sonarqube/bin/linux-x86-64/sonar.sh stop

User=sonarqube
Group=sonarqube
PermissionsStartOnly=true
Restart=always

StandardOutput=syslog
LimitNOFILE=131072
LimitNPROC=8192
TimeoutStartSec=5
SuccessExitStatus=143

[Install]
WantedBy=multi-user.target
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable SonarQube at system startup:

```bash
sudo systemctl enable sonarqube
```

Start SonarQube:

```bash
sudo systemctl start sonarqube
```

> The service must only be started after completing the configuration and resource-limit steps above.

---

## 3.3.9 Cracking SonarQube

Before starting the sonarqube service (systemctl start sonarqube) open the `/opt/sonarqube/lib/sonar-application-2026.3.0.123014.jar` with file roller and change the following:

#### 1. Replace the `com/sonarsource/M/A.class` with the corresponding file inside the Crack folder.
- Original Size: 1.3kB
- New Size: 2.3kB

#### 2. Replace the `com/sonar/S/k.class` with the corresponding file inside the Crack folder.
- Original Size: 1.3kB
- New Size: 2.3kB

#### 3. Replace the `com/sonar/S/k$_A.class` with the corresponding file inside the Crack folder.
- Original Size: 169 bytes
- New Size: 193 bytes

#### 4. Replace the `com/sonar/S/k$_k.class` with the corresponding file inside the Crack folder.
- Original Size: 1.1kB
- New Size: 1.3kB

**Note: After changing, re-open the file to make sure changes were made successfully.**

After replacing the files above, proceed with `systemctl start sonarqube` and head to `http://localhost:9000` (it might take about a minute or more for web-panel to come up).

Open the License page and add the following string as the License:
```copy
Iw0KI01vbiBBdWcgMDQgMTU6NDk6MzggRUVTVCAyMDI1DQpDb21wYW55PVJVLUJPQVJEDQpUeXBlPVBST0RVQ1RJT04NClNlcnZlcklkPSoNClN1cHBvcnQ9dHJ1ZQ0KRGlnZXN0PU1DMENGR0F0VlQvT1poT3pDekFnaEhrWkRNK3ZCM0lvQWhVQWtzQStPQkZpeXJmQkpHd1VHbVFaWlJ2N3B2a1w9DQpFeHBpcmF0aW9uPTIwMzAtMTItMzENCkZlYXR1cmVzPVZ1bG5lcmFiaWxpdHkgQW5hbHlzaXMsSGlnaCBBdmFpbGFiaWxpdHksQW5hbHlzaXMgb2YgQVBFWCxBbmFseXNpcyBvZiBKYXZhLEFuYWx5c2lzIG9mIEphdmFTY3JpcHQsQW5hbHlzaXMgb2YgQ1xcXCMsQW5hbHlzaXMgb2YgVHlwZVNjcmlwdCxBbmFseXNpcyBvZiBGbGV4LEFuYWx5c2lzIG9mIFB5dGhvbixBbmFseXNpcyBvZiBQSFAsQW5hbHlzaXMgb2YgWE1MLEFuYWx5c2lzIG9mIFdlYixCcmFuY2ggQW5hbHlzaXMsU29uYXJMaW50IFNtYXJ0IE5vdGlmaWNhdGlvbnMsUG9ydGZvbGlvcyBNYW5hZ2VtZW50LEV4ZWN1dGl2ZSBSZXBvcnRpbmcsUHJvamVjdCBUcmFuc2ZlcixQYXJhbGxlbCBQcm9jZXNzaW5nLEFuYWx5c2lzIG9mIEFCQVAsQW5hbHlzaXMgb2YgQy9DKyssQW5hbHlzaXMgb2YgT2JqZWN0aXZlLUMsQW5hbHlzaXMgb2YgUEwvU1FMLEFuYWx5c2lzIG9mIFN3aWZ0LEFuYWx5c2lzIG9mIFQtU1FMLEFuYWx5c2lzIG9mIFZCLk5FVCxBbmFseXNpcyBvZiBDT0JPTCxBbmFseXNpcyBvZiBQTC9JLEFuYWx5c2lzIG9mIFJQRyxBbmFseXNpcyBvZiBWQjYsQWR2YW5jZWQgU2VjdXJpdHksU0NBDQpFZGl0aW9uPWRhdGFjZW50ZXINCkVkaXRpb25MYWJlbD1EYXRhIENlbnRlcg0KTWF4TG9jPTkyMjMzNzIwMzY4NTQ3NzU4MDcNClBsdWdpbnM9bGljZW5zZSxicmFuY2gsZGV2ZWxvcGVyLGVudGVycHJpc2UsZ292ZXJuYW5jZSxhcGV4LGFiYXAsY3BwLHBsc3FsLHN3aWZ0LHRzcWwsdmJuZXQsY29ib2wscGxpLHJwZyx2YixnbyxweXRob24scGhwLGphdmEsZGF0YWNlbnRlci1lZGl0aW9uLGNlLXdvcmtlcnMsZGV2ZWxvcGVyLXNjYW5uZXIsZGV2ZWxvcGVyLXNlcnZlcixoYSxzZWN1cml0eXJlcG9ydCxtb25pdG9yaW5nLHNjaW0sZ2l0bGFiLXZ1bG5lcmFiaWxpdHktcmVwb3J0LGFuYWx5c2lzLWljdSxhbmFseXNpcy1rdXJvbW9qaSxhbmFseXNpcy1ub3JpLGFuYWx5c2lzLXBob25ldGljLGFuYWx5c2lzLXNtYXJ0Y24sYW5hbHlzaXMtc3RlbXBlbCxhbmFseXNpcy11a3JhaW5pYW4sZGlzY292ZXJ5LWF6dXJlLWNsYXNzaWMsZGlzY292ZXJ5LWVjMixkaXNjb3ZlcnktZ2NlLGluZ2VzdC1hdHRhY2htZW50LG1hcHBlci1hbm5vdGF0ZWQtdGV4dCxtYXBwZXItbXVybXVyMyxtYXBwZXItc2l6ZSxyZXBvc2l0b3J5LWF6dXJlLHJlcG9zaXRvcnktZ2NzLHJlcG9zaXRvcnktaGRmcyxyZXBvc2l0b3J5LXMzLHN0b3JlLXNtYix0cmFuc3BvcnQtbmlvLGNheWMsY2ZhbWlseSxjc2hhcnAsZGJkLWphdmEtZnJvbnRlbmQsZGJkLGRiZC1weXRob24tZnJvbnRlbmQsZmxleCxodG1sLGlhYyxqYWNvY28samF2YXNjcmlwdCxrb3RsaW4scnVieSxzY2FsYSxzZWN1cml0eS1jc2hhcnAtZnJvbnRlbmQsc2VjdXJpdHktamF2YS1mcm9udGVuZCxzZWN1cml0eS1qcy1mcm9udGVuZCxzZWN1cml0eS1waHAtZnJvbnRlbmQsc2VjdXJpdHksc2VjdXJpdHktcHl0aG9uLWZyb250ZW5kLHRleHQtZW50ZXJwcmlzZSx0ZXh0LHhtbCxhcmNoaXRlY3R1cmUtamF2YS1mcm9udGVuZCxhcmNoaXRlY3R1cmUsY2ZhbWlseS1kZXBlbmRlbmNpZXMsY3NoYXJwLWVudGVycHJpc2UsZGFydCxpYWMtZW50ZXJwcmlzZSxqYXZhLXN5bWJvbGljLWV4ZWN1dGlvbixqY2wsdmJuZXQtZW50ZXJwcmlzZSxhcmNoaXRlY3R1cmUtamF2YXNjcmlwdC1mcm9udGVuZCxnby1lbnRlcnByaXNlLGphc21pbixydXN0LHNlY3VyaXR5LWdvLWZyb250ZW5kLHNlY3VyaXR5LXZibmV0LWZyb250ZW5kLHRleHQtZW50ZXJwcmlzZSxzY2EsYWR2YW5jZWQtc2VjdXJpdHkNCg==
```

---
## 3.3.10 Verify SonarQube

Check the service status:

```bash
sudo systemctl status sonarqube
```

Check that SonarQube is listening on port `9000`:

```bash
ss -lntp | grep 9000
```

The SonarQube web interface should be available at:

```text
http://localhost:9000
```

Verify SonarScanner:

```bash
sonar-scanner -v
```

At this stage, both the SonarQube server and SonarScanner CLI are ready for project analysis.

---


## 3.4 CodeQL CLI

Download the CodeQL CLI:

```bash
wget https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip
```

Extract the archive:

```bash
unzip codeql-linux64.zip
```

Move CodeQL to `/opt`:

```bash
sudo mv codeql /opt/codeql
```

Add CodeQL to the PATH:

```bash
nano ~/.bashrc
```

Add:

```bash
export PATH=$PATH:/opt/codeql
```

Reload the shell configuration:

```bash
source ~/.bashrc
```

Verify the installation:

```bash
codeql version
```

---

## 3.5 CodeQL Query Packs

The CodeQL CLI provides the analysis engine, while language-specific query packs are distributed separately.

The required query packs were downloaded using:

```bash
codeql pack download codeql/cpp-queries
codeql pack download codeql/csharp-queries
codeql pack download codeql/java-queries
codeql pack download codeql/javascript-queries
codeql pack download codeql/python-queries
codeql pack download codeql/go-queries
codeql pack download codeql/ruby-queries
codeql pack download codeql/swift-queries
codeql pack download codeql/rust-queries
codeql pack download codeql/actions-queries
```

Downloaded packs are stored in:

```text
~/.codeql/packages
```

Verify the installed packs:

```bash
codeql resolve packs
```

Verify supported languages:

```bash
codeql resolve languages
```

Expected languages include:

```text
cpp
java
javascript
python
go
csharp
ruby
swift
rust
actions
```

### Query Pack Issue

Some optional query packs, such as:

```text
xml-queries
yaml-queries
properties-queries
```

may return:

```text
HTTP 403 Forbidden
```

These packs were not required for the BIRD C/C++ analysis and were therefore not used.

---

# 4. BIRD v2.17.1 Repository Setup

## 4.1 Create the Workspace

Create a dedicated directory for the analysis projects:

```bash
mkdir -p ~/Projects
cd ~/Projects
```

---

## 4.2 Download BIRD v2.17.1

The Git repository could not be cloned successfully in the current environment because of Git connectivity issues.

Therefore, the official GitHub source archive was downloaded instead:

```bash
wget https://github.com/CZ-NIC/bird/archive/refs/tags/v2.17.1.zip
```

---

## 4.3 Extract the Source Code

```bash
unzip bird-v2.17.1.zip
```

Enter the extracted project:

```bash
cd bird-2.17.1
```

Verify the current directory:

```bash
pwd
```

Example:

```text
/home/<user>/Projects/bird-2.17.1
```

Verify the source tree:

```bash
ls
```

Expected directories/files include:

```text
configure.ac
README
INSTALL
NEWS
client/
conf/
filter/
lib/
nest/
proto/
sysdep/
```

---

# 5. Generate the Configure Script

Because the source was obtained from a GitHub ZIP archive, the generated `configure` script was not available.

Generate it using Autotools:

```bash
autoreconf -fi
```

This generates the required configuration files, including:

```text
configure
```

### Warning Encountered

The following warning was displayed:

```text
warning: The macro 'AC_PROG_CC_C99' is obsolete.
```

This is an Autotools warning and did not prevent configuration or compilation.

No modification was required.

---

# 6. Configure BIRD

Run:

```bash
./configure
```

The configuration process checks the available compiler, libraries, system features and supported routing protocols.

If configuration succeeds, files such as the following are generated:

```text
Makefile
config.status
obj/sysdep/autoconf.h
```

The configured project included support for multiple routing protocols, including:

```text
Aggregator
BFD
Babel
BGP
L3VPN
MRT
OSPF
PERF
PIPE
RADV
RIP
RPKI
Static
```

---

# 7. Build BIRD

Compile the project using all available CPU cores:

```bash
make -j$(nproc)
```

Verify that the build completed successfully.

Expected executables include:

```text
bird
birdc
birdcl
```

---

# 8. Build Issues Encountered

## 8.1 `write()` Return-Value Warning

The compiler reported a warning similar to:

```text
warning: ignoring return value of 'write'
```

### Cause

The return value of the `write()` system call is not checked in the corresponding source code.

### Resolution

No change was made to the source code at this stage.

The warning did not prevent the build from completing and was retained as a compiler/build warning for later static-analysis review.

---

# 9. Static Analysis Tool Execution

This section documents the commands used to execute the static analysis tools on BIRD v2.17.1 and generate the analysis reports.

---

# 9.1 Project Preparation

Enter the BIRD project directory:

```bash
cd ~/Projects/bird-2.17.1
```

Create dedicated directories for analysis reports:

```bash
mkdir -p reports/{cppcheck,semgrep,codeql,external}
```

---

# 9.2 Additional Analysis Utilities

Two additional utilities were used during the analysis:

* **Bear** – generates the compilation database (`compile_commands.json`)
* **jq** – inspects and filters JSON/SARIF files

Install them if they are not already available:

```bash
sudo apt install -y bear jq
```

Verify:

```bash
bear --version
jq --version
```

---

# 10. Cppcheck Analysis

## 10.1 Generate Compilation Database

The BIRD project was rebuilt through Bear to capture the actual compiler commands:

```bash
bear -- make -j1
```

This generates:

```text
compile_commands.json
```

The compilation database contains:

* Source files
* Compiler commands
* Include directories
* Compiler flags
* Preprocessor definitions

Verify the number of compilation commands:

```bash
jq 'length' compile_commands.json
```

---

## 10.2 Run Cppcheck

The final Cppcheck configuration used the compilation database and focused on warning, performance, and portability checks:

```bash
cppcheck \
  --project=compile_commands.json \
  --enable=warning,performance,portability \
  --inconclusive \
  -j1 \
  --xml \
  --xml-version=2 \
  2> reports/cppcheck/cppcheck.xml
```

### Important Options

| Option                                     | Purpose                                  |
| ------------------------------------------ | ---------------------------------------- |
| `--project=compile_commands-analysis.json` | Uses the actual compilation commands     |
| `--enable=warning,performance,portability` | Enables the selected analysis categories |
| `--inconclusive`                           | Reports lower-confidence findings        |
| `-j1`                                      | Uses a single analysis thread            |
| `--xml`                                    | Generates XML output                     |
| `--xml-version=2`                          | Uses Cppcheck XML schema version 2       |

---

## 10.3 Verify Cppcheck Results

Count all findings:

```bash
grep -c '<error ' \
  reports/cppcheck/cppcheck.xml
```

Count findings by severity:

```bash
grep '<error ' reports/cppcheck/cppcheck.xml \
| sed -n 's/.*severity="\([^"]*\)".*/\1/p' \
| sort \
| uniq -c
```

Count findings by rule:

```bash
grep '<error ' reports/cppcheck/cppcheck.xml \
| sed -n 's/.*id="\([^"]*\)".*/\1/p' \
| sort \
| uniq -c \
| sort -nr
```

Final report:

```text
reports/cppcheck/cppcheck.xml
```

Final verified findings:

```text
119
```
## 10.4 Scope Filtering

Instead of restricting the compilation database before running Cppcheck, the complete Cppcheck output is generated first and then filtered based on the required source scope.

The intended source scope is:
```text
client/
conf/
filter/
lib/
nest/
proto/
sysdep/
```
The filtering is performed using the following script located in the scripts directory:


[filter_cppcheck_scope.py](scripts/filter_cppcheck_scope.py)


Run the scope filter:
```bash
python3 scripts/filter_cppcheck_scope.py \
  reports/cppcheck/cppcheck.xml \
  reports/cppcheck/cppcheck-final.xml
```
The script keeps Cppcheck findings whose locations belong to the defined source scope and removes findings outside the scope.

Verify the Filtered Result
```bash
echo "Before:"
grep -c '<error ' reports/cppcheck/cppcheck.xml


echo "After:"
grep -c '<error ' reports/cppcheck/cppcheck-final.xml
```
For the final analysis:
```text
Before: 119
After:  113
```
No findings were removed because all findings in the generated Cppcheck report were already within the required source scope.

An additional scope verification was performed to ensure that no locations outside the allowed directories remained in the filtered report.

---

# 11. Semgrep Analysis

## 11.1 Semgrep Automatic Ruleset

Run Semgrep using the automatic ruleset:

```bash
semgrep scan \
  --config auto \
  --include='*.c' \
  --include='*.h' \
  --sarif \
  --output reports/semgrep/semgrep-auto.sarif \
  client conf filter lib nest proto sysdep
```
### Command Options

| Argument | Description |
|----------|-------------|
| `semgrep scan` | Starts a Semgrep scan. |
| `--config auto` | Uses Semgrep's automatic ruleset to select applicable rules for the analyzed code. |
| `--include='*.c'` | Limits the scan to C source files. |
| `--include='*.h'` | Limits the scan to C header files. |
| `--sarif` | Generates the analysis results in SARIF format. |
| `--output reports/semgrep/semgrep-auto.sarif` | Saves the SARIF results to the specified output file. |
| `client conf filter lib nest proto sysdep` | Specifies the BIRD source directories to be analyzed. |


Generated report:

```text
reports/semgrep/semgrep-auto.sarif
```

Verify the number of results:

```bash
jq '.runs[].results | length' \
  reports/semgrep/semgrep-auto.sarif
```

Final result:

```text
0 findings
```

---

## 11.2 Semgrep Security Audit Ruleset

Run the security-focused Semgrep ruleset:

```bash
semgrep scan \
  --config p/security-audit \
  --include='*.c' \
  --include='*.h' \
  --sarif \
  --output reports/semgrep/security-audit.sarif \
  client conf filter lib nest proto sysdep
```

Generated report:

```text
reports/semgrep/security-audit.sarif
```

Verify the results:

```bash
jq '.runs[].results | length' \
  reports/semgrep/security-audit.sarif
```

Final result:

```text
42 findings
```

---

# 12. CodeQL Analysis

## 12.1 Create CodeQL Database

Before creating the CodeQL database, the previous build artifacts were removed to ensure a clean build.

```bash
make clean
```

Create a CodeQL database for the BIRD C/C++ source code:

```bash
codeql database create bird-db \
  --language=cpp \
  --source-root=. \
  --command="make -j$(nproc)"
```

The database is generated in:

```text
bird-db/
```

---

## 12.2 Verify CodeQL Query Packs

Check the installed query packs:

```bash
codeql resolve packs
```

The C/C++ query pack must be available:

```text
codeql/cpp-queries
```

---

## 12.3 Run the C/C++ Security and experimental Suite

Run the default CodeQL C/C++ security and experimental query suite:

```bash
codeql database analyze bird-db \
  codeql/cpp-queries:codeql-suites/cpp-security-experimental.qls \
  --format=sarif-latest \
  --output=reports/codeql/codeql.sarif
```

Generated report:

```text
reports/codeql/codeql.sarif
```

Verify the number of results:

```bash
jq '.runs[].results | length' \
  reports/codeql/codeql.sarif
```

---

## 12.4 Filter CodeQL Results to the Analysis Scope

The CodeQL SARIF output was filtered to keep findings located in the main BIRD source directories:

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
' reports/codeql/codeql.sarif \
> reports/codeql/codeql-final.sarif
```

Count the final results:

```bash
jq '.runs[].results | length' \
  reports/codeql/codeql-final.sarif
```

Final verified result:

```text
82 findings
```

Show findings grouped by source file:

```bash
jq -r '
  .runs[].results[]
  | .locations[0].physicalLocation.artifactLocation.uri
' reports/codeql/codeql-final.sarif \
| sort \
| uniq -c \
| sort -nr
```

Final report:

```text
reports/codeql/codeql-final.sarif
```

---

# 13. Running SonarQube with Build Context

## 13.1 Create SonarQube Project

A new project was created in the SonarQube dashboard.

Project information:

| Property | Value |
|----------|-------|
| Project Name | `bird-2.17.1` |
| Project Key | `bird-2.17.1` |
| Version | `2.17.1` |

The default **New Code Definition** settings were used.

---

## 13.2 Generate Authentication Token

A SonarQube authentication token was generated from:

```text
My Account → Security → Generate Token
```
The generated token was used by SonarScanner to authenticate with the SonarQube server.

The token was configured in sonar-project.properties and should not be committed to the repository.

## 13.3 Download and Install Build Wrapper

The SonarQube Build Wrapper was downloaded directly from the local SonarQube server:

```bash
wget http://localhost:9000/static/cpp/build-wrapper-linux-x86.zip
```
Extract the archive:

```bash
unzip build-wrapper-linux-x86.zip
```

Move the Build Wrapper to /opt:

```bash
sudo mv build-wrapper-linux-x86 /opt/
```
Create a global symbolic link:

```bash
sudo ln -s \
  /opt/build-wrapper-linux-x86/build-wrapper-linux-x86-64 \
  /usr/local/bin/build-wrapper-linux-x86-64
```
Verify the installation:
```bash
build-wrapper-linux-x86-64 --help
```

## 13.4 Capture the BIRD Build

Remove previous build artifacts:
```bash
make clean
```
Run the BIRD build through Build Wrapper:
```bash
build-wrapper-linux-x86-64 \
  --out-dir bw-output \
  make -j1
```
The -j1 option was used to perform a single-threaded build and ensure that all compilation commands were captured correctly.

## 13.5 Verify Build Wrapper Output

The Build Wrapper generated the following files:
```text
bw-output/
├── build-wrapper-dump.json
├── build-wrapper.log
└── compile_commands.json
```

Verify the generated build context:
```bash
ls -lh bw-output/build-wrapper-dump.json
```
The captured information includes:

* Compiler commands
* Source files
* Include directories
* Compiler flags
* Preprocessor definitions
* Compilation units

## 13.6 Configure SonarQube

The following configuration was added to **sonar-project.properties**:

```properties
sonar.projectKey=bird-2.17.1
sonar.projectName=bird-2.17.1
sonar.projectVersion=2.17.1


sonar.sources=.
sonar.sourceEncoding=UTF-8


sonar.host.url=http://localhost:9000
sonar.token=<YOUR_TOKEN>


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
reports/**,\
.venv/**,\
**/*.py

```

The following property enables SonarQube to use the C/C++ compilation context captured by Build Wrapper:
```text
sonar.cfamily.build-wrapper-output=bw-output
```

The following directories were excluded from the SonarQube source analysis:
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
The main BIRD source directories remained in the analysis scope:
```text
client/
conf/
filter/
lib/
nest/
proto/
sysdep/
```

## 13.7 Run SonarScanner

Run the SonarQube analysis:
```bash
sonar-scanner
```

The analysis results were uploaded to the local SonarQube server:
```bash
http://localhost:9000
```

## 13.8 Review the SonarQube Dashboard

After the analysis completed, the bird-2.17.1 project was opened in the SonarQube dashboard.

The following sections were reviewed:

* Overview – Overall project metrics
* Issues – Bugs, vulnerabilities, and code smells
* Security Hotspots – Security-sensitive findings requiring manual review
* Rules – Rules responsible for reported findings
* Source Code – Navigation to the affected source files and lines

The Build Wrapper provided SonarQube with the actual compilation context, including compiler options, include paths, macros, and compiled source files.

This resulted in a more accurate C/C++ analysis and reduced findings caused by incomplete compilation information.

---

# 14. Analysis Results

The verified results at this stage were:

| Tool     | Configuration               | Findings |
| -------- | --------------------------- | -------: |
| Cppcheck | Scope Filtering             |  **113** |
| Semgrep  | Automatic ruleset           |    **0** |
| Semgrep  | Security Audit              |   **42** |
| CodeQL   | C/C++ Security and experimental  |  **82** |


---

# 15. Normalize External Tool Results into SonarQube

## 15.1 Objective

The outputs generated by Semgrep, CodeQL, and Cppcheck were converted into the SonarQube External Issues JSON format.

The converted reports were then configured as external issues and imported into a single SonarQube project for unified analysis.

---

## 15.2 Create Required Directories

Create directories for the conversion scripts and generated external reports:

```bash
mkdir -p scripts
mkdir -p reports/external
```
The resulting structure is:
```text
scripts/
├── semgrep_to_sonar.py
├── codeql_to_sonar.py
└── cppcheck_to_sonar.py

reports/
├── semgrep/
├── codeql/
├── cppcheck/
└── external/
```
The conversion scripts are available in the repository:

* [semgrep_to_sonar.py](scripts/semgrep_to_sonar.py)
* [codeql_to_sonar.py](scripts/codeql_to_sonar.py)
* [cppcheck_to_sonar.py](scripts/cppcheck_to_sonar.py)

## 15.3 Convert Semgrep Results

Automatic Ruleset

Convert the Semgrep automatic analysis results:
```bash
python3 scripts/semgrep_to_sonar.py \
  reports/semgrep/semgrep-auto.sarif \
  reports/external/semgrep-auto.json \
  Semgrep
```

Security Audit Ruleset

Convert the Semgrep security-audit results:

```bash
python3 scripts/semgrep_to_sonar.py \
  reports/semgrep/security-audit.sarif \
  reports/external/semgrep-security.json \
  Semgrep
```

## 15.4 Convert CodeQL Results

Convert the CodeQL SARIF report into SonarQube External Issues format:
```bash
python3 scripts/codeql_to_sonar.py \
  reports/codeql/codeql-final.sarif \
  reports/external/codeql.json
```

## 15.5 Convert Cppcheck Results

Convert the Cppcheck XML report into SonarQube External Issues format:
```bash
python3 scripts/cppcheck_to_sonar.py \
  reports/cppcheck/cppcheck-final.xml \
  reports/external/cppcheck.json
```

## 15.6 Configure SonarQube External Reports

The generated external issue reports were added to the **sonar-project.properties**  configuration.
```properties
sonar.externalIssuesReportPaths=\
reports/external/codeql.json,\
reports/external/semgrep-security.json,\
reports/external/semgrep-auto.json,\
reports/external/cppcheck.json
```

This configuration instructs SonarQube to import the findings generated by the external static analysis tools.

## 15.7 Run SonarScanner

Run the SonarQube analysis:
```bash
sonar-scanner
```
During the analysis, SonarQube imported the external issues from the generated JSON reports.

---

# 16. SonarQube Findings Export and Merge

## 16.1 Objective

The SonarQube findings were exported and consolidated to create a single dataset containing **Reliability**, **Security**, and **Security Hotspots** findings.
The resulting consolidated dataset was then enriched with **CWE metadata** from CodeQL, Cppcheck, SonarQube, and Semgrep. This enriched dataset is used as input for the later LLM-assisted triage stage.

---

## 16.2 Export Security and Reliability Findings

Because the number of SonarQube issues can exceed the API page size, findings were retrieved page by page using the SonarQube Issues API with a page size of 500.

The export script:

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
```text
RELIABILITY: 196
SECURITY:    130
TOTAL:       326
```
---

## 16.3 Export Security Hotspots

Security Hotspots are retrieved separately using the SonarQube Hotspots API.

Run:
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

The generated file is:
```text
reports/sonarqube/sonarqube-hotspots.json
```

## 16.4 Merge SonarQube Findings

The Security/Reliability findings and Security Hotspots were merged into a single JSON dataset.

The merge script:

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
The resulting consolidated dataset contains:
```text

Reliability:       196
Security:          130
Security Hotspots:  81
-----------------------
Total:             407
```

The external findings generated by CodeQL, Cppcheck, and Semgrep are represented in the overall SonarQube-based analysis as external issues. Their source-specific counts are not added again to the 407 consolidated candidates.

---

# 17. CWE Metadata Enrichment

## 17.1 Objective

The consolidated findings were enriched with **Common Weakness Enumeration (CWE)** metadata.
CWE information was obtained from the metadata available for each analysis tool and added to the corresponding findings without removing findings for which a CWE mapping was unavailable.

The enriched dataset is:

```text
reports/sonarqube/merged_candidates_with_cwe.json
```
---

## 17.2 Add CWE Metadata to CodeQL Findings

CodeQL findings in merged_candidates.json were enriched using CWE information from the CodeQL query metadata.

The enrichment script is:

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

The original finding information is preserved, while the CWE metadata is added as additional context for later LLM triage.

---

## 17.3 Add CWE Metadata to Cppcheck Findings

Cppcheck findings were enriched using CWE mappings from the Cppcheck rule metadata.

The metadata file is:

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


Therefore, missing CWE metadata does not cause a Cppcheck finding to be removed.

---
## 17.4 Add CWE Metadata to SonarQube Findings

SonarQube-originated findings were enriched using rule metadata retrieved from the SonarQube API.

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
---

## 17.5 Verify Security Hotspot CWE Metadata

Security Hotspots were already included in the consolidated dataset during the merge stage.

Their CWE metadata was verified separately.

The consolidated file contained:
```text
Findings with ruleKey: 81
With CWE:             81
Without CWE:           0
```
The 81 Security Hotspots were associated with the following SonarQube rules:
```text
c:S5816: 13
c:S5813: 41
c:S5801: 27
```
All three rules were mapped to:
```text
CWE-120
```
Thus, all Security Hotspots in the consolidated dataset had CWE metadata available.

---
## 17.6 Add CWE Metadata to Semgrep Findings

Semgrep findings were enriched using CWE information from the Semgrep rule metadata.

The enrichment script is:

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

All 42 Semgrep findings were successfully enriched with CWE metadata.

---
## 17.7 Final Enriched Dataset

After the CWE enrichment steps, the consolidated findings are available in:

reports/sonarqube/merged_candidates_with_cwe.json

This file preserves the original findings while adding CWE metadata where a valid mapping is available.

The enriched CWE field provides additional security context for the subsequent LLM-assisted false-positive triage stage.

---
# 18. BIRD Tag and Call Graph Setup

This section describes the commands used to generate **CTags symbol information** and the **LLVM Call Graph** for BIRD v2.17.1.

The generated symbol and call-graph information was used to provide additional source-code context during the manual review and false-positive analysis of static-analysis findings.

---

## 18.1 Install Universal Ctags

Install Universal Ctags:

```bash
sudo apt install universal-ctags
```
Verify the installation:

```bash
ctags --version
```

## 18.2 Generate CTags

Navigate to the BIRD source directory:
```bash
cd ~/Projects/bird-2.17.1
```
Generate the tags file:

```bash
ctags -R \
  --languages=C,C++ \
  --c-kinds=+p \
  --fields=+n \
  -f tags .
```
Verify the generated tags:

```bash
ls -lh tags
head -20 tags
wc -l tags
```


The generated tags file provides symbol information such as:

* Functions
* Structures
* Macros
* Other C/C++ symbols

This information was later used by the batch-processing scripts to obtain additional context for reported findings.

## 18.3 Install WLLVM

Install WLLVM:

```bash
pip install wllvm
```

Verify:

```bash
which wllvm
which extract-bc
```
## 18.4 Configure LLVM/WLLVM

Configure WLLVM to use Clang:
```bash
export LLVM_COMPILER=clang
export CC=wllvm
```
Verify the environment variables:
```bash
echo $LLVM_COMPILER
echo $CC
```
Verify the installed LLVM tools:
```bash
clang --version
llvm-config --version
```
## 18.5 Rebuild BIRD with WLLVM

Navigate to the BIRD source directory:
```bash
cd ~/Projects/bird-2.17.1
```
Clean the previous build:
```bash
make clean
```
Regenerate the configuration files:
```bash
autoreconf -fi
```
Configure the project:
```bash
./configure
```
Build BIRD using WLLVM:

```bash
make
```
## 18.6 Extract LLVM Bitcode

After the build completes, extract the LLVM bitcode from the generated BIRD executable:
```bash
extract-bc bird
```
Verify the generated bitcode:
```bash
ls -lh bird.bc
file bird.bc
```
The resulting bird.bc file contains the LLVM intermediate representation required for subsequent LLVM analysis.

## 18.7 Generate the LLVM Call Graph

Verify the installed LLVM opt version:
```bash
opt --version
```
Generate the LLVM call graph:
```bash
opt --disable-output --passes=dot-callgraph bird.bc
```
This generates:

```text
bird.bc.callgraph.dot
```
Verify the generated file:
```bash
ls -lh *.dot
find . -maxdepth 1 -name "*.dot" -print
head -20 bird.bc.callgraph.dot
```
## 18.8 Count Call Graph Nodes and Edges

Count the nodes:
```bash
grep -c 'Node0x' bird.bc.callgraph.dot
```
Count the edges:
```bash
grep -c -- '->' bird.bc.callgraph.dot
```
For the BIRD v2.17.1 build, the generated call graph contained approximately:
```text
Nodes: 9534
Edges: 7549
```
---

# 19. False Positive Reduction Approach

During the static analysis of BIRD v2.17.1, several techniques were applied to reduce false-positive findings and improve the relevance of the reported results.

The following approaches were used:

- **Build and Compilation Context:** SonarQube Build Wrapper and the `compile_commands.json` generated by Bear were used to provide the analyzers with the actual compilation context, including compiler options, include paths, preprocessor definitions, and compiled source files. This helped reduce findings caused by incomplete or incorrect build information.
- **Analysis Scope Filtering:** Source directories and generated files that were not relevant to the analysis were excluded. CodeQL results were also filtered to keep findings within the defined BIRD source scope. Similar scope restrictions were applied to the other tools where appropriate.
- **Focused Rule Sets:** Cppcheck and Semgrep were configured with more targeted rule sets to reduce low-value informational and style-related findings and focus on more relevant security and reliability issues.
- **CTags:** A CTags symbol database was generated to provide function, structure, macro, and symbol information for additional finding context.
- **LLVM Call Graph:** An LLVM call graph was generated to understand relationships between functions and determine whether reported code is reachable and how it is used within the program.

These techniques reduced analysis noise and provided additional context for manually reviewing the remaining findings. The resulting information was also used to enrich findings before performing LLM-assisted false-positive analysis.

---
