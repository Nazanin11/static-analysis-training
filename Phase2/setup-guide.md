# Environment Setup Documentation


**Operating System:** Ubuntu 24.04.4 LTS (Dual Boot)

**Date:** July 2026

---

# Objective

The goal of this setup was to prepare the environment for static code analysis using the following tools:

- SonarQube
- SonarScanner
- CodeQL
- Semgrep
- Cppcheck

---

# System Information

```bash
lsb_release -a
uname -a
```

Output:

- Ubuntu 24.04.4 LTS
- Linux Kernel 7.0
- x86_64 Architecture

---

# Installing Required Packages

First, the system package list was updated.

```bash
sudo apt update
sudo apt upgrade -y
```

Then the required development packages were installed.

```bash
sudo apt install -y \
git \
curl \
wget \
unzip \
zip \
build-essential \
python3 \
python3-pip \
python3-venv \
pipx \
openjdk-17-jdk
```

---

# Installing Semgrep

Semgrep was installed using **pipx**.

```bash
pipx install semgrep
```

Verify installation:

```bash
semgrep --version
```

Result:

```
Semgrep 1.170.0
```

### Issue Encountered

Installing with pip failed because Ubuntu 24.04 uses an externally managed Python environment.

```
error: externally-managed-environment
```

### Solution

Installed Semgrep using **pipx** instead of pip.

---

# Installing Cppcheck

Cppcheck was installed from the Ubuntu repository.

```bash
sudo apt install cppcheck
```

Verify installation.

```bash
cppcheck --version
```

Result

```
Cppcheck 2.13.0
```

---

# Installing SonarQube 

The SonarQube Community Edition was installed by following the official installation guide below:

https://www.centron.de/en/tutorial/how-to-install-sonarqube-on-ubuntu-24-04-step-by-step-guide/

The installation was performed on Ubuntu 24.04 LTS using the native installation method (without Docker). The following main steps from the guide were completed:

- Installed PostgreSQL
- Created the PostgreSQL database and user
- Installed OpenJDK 17
- Downloaded and extracted SonarQube
- Created a dedicated `sonarqube` system user
- Configured the `sonar.properties` file
- Installed and configured SonarScanner CLI
- Created a systemd service for SonarQube
- Started the SonarQube service and verified that it was running
- Accessed the SonarQube web interface successfully

## Configuration Changes

The following values were modified during the installation:

```properties
sonar.jdbc.username=sonaruser
sonar.jdbc.password=********
sonar.jdbc.url=jdbc:postgresql://localhost:5432/sonarqube

sonar.web.host=127.0.0.1
sonar.web.port=9000
```

## Steps Not Performed

The following parts of the tutorial were intentionally skipped because they were not required for this project:

- Firewall (UFW) configuration
- Nginx reverse proxy configuration
- Example project analysis from the tutorial
- Creating additional SonarQube users
- Generating API tokens before they were needed
- Server reboot after installation

SonarQube was successfully installed and is accessible locally at:

```
http://localhost:9000
```
---

# Installing CodeQL

Download the CodeQL CLI.

```bash
wget https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip
```

Extract the archive.

```bash
unzip codeql-linux64.zip
```

Move it to the installation directory.

```bash
sudo mv codeql /opt/codeql
```

Add CodeQL to the PATH.

```bash
nano ~/.bashrc
```

Append the following line.

```bash
export PATH=$PATH:/opt/codeql
```

Reload the shell.

```bash
source ~/.bashrc
```

Verify installation.

```bash
codeql version
```
## Downloading CodeQL Query Packs

The CodeQL CLI provides the analysis engine, while the language-specific query packs are distributed separately. These packs were downloaded after installing the CLI.

Download the required query packs:

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

Downloaded query packs are stored in:

```text
~/.codeql/packages
```

Verify that the packs are available:

```bash
codeql resolve packs
```

Verify the supported languages:

```bash
codeql resolve languages
```

Example output:

```
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

## Notes

- The CodeQL CLI installation does not include all query packs by default.
- Query packs are downloaded automatically into the local package cache (`~/.codeql/packages`).
- Some optional packs (such as `xml-queries`, `yaml-queries`, and `properties-queries`) are not publicly available and may return **HTTP 403 Forbidden** when downloaded. These packs are not required for analyzing C/C++ projects.
- The downloaded packs are reused for future analyses and normally do not need to be downloaded again.
---