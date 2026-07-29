# BIRD v2.17.1 Repository Setup

**Date:** July 2026

## Objective

The purpose of this document is to prepare the BIRD routing daemon source code for static analysis using the following tools:

- SonarQube
- CodeQL
- Semgrep
- Cppcheck

The required version for this project is **BIRD v2.17.1**.

---

# Repository Information

| Item | Value |
|------|------|
| Project | BIRD Routing Daemon |
| Repository | https://github.com/CZ-NIC/bird |
| Version | v2.17.1 |
| Acquisition Method | GitHub Source Archive (ZIP) |

---

# Downloading the Source Code

The Git repository could not be cloned successfully in the current environment due to Git connectivity issues. Therefore, the official GitHub source archive for **v2.17.1** was downloaded instead.

## Create the workspace

```bash
mkdir -p ~/Projects
cd ~/Projects
```

## Download the source archive

```bash
wget https://github.com/CZ-NIC/bird/archive/refs/tags/v2.17.1.zip
```

## Extract the archive

```bash
unzip bird-v2.17.1.zip
```

## Enter the project directory

```bash
cd bird-2.17.1
```

## Verify the current directory

```bash
pwd
```

Example output:

```text
/home/nazanin/Projects/bird-2.17.1
```

## Verify the repository contents

```bash
ls
```

The extracted source contains files such as:

```
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

# Generating the Configure Script

The GitHub source archive contains the `configure.ac` file but does not include the generated `configure` script.

To generate the required build configuration files, the following command was executed:

```bash
autoreconf -fi
```

### Output

The command completed successfully and generated the `configure` script.

A warning was displayed:

```text
warning: The macro 'AC_PROG_CC_C99' is obsolete.
```

This is an informational warning from Autotools and does not affect the build process.

---

# Configuring the Project

After generating the `configure` script, the project was configured.

```bash
./configure
```

## Result

The configuration completed successfully.

The following files were generated:

- `Makefile`
- `config.status`
- `obj/sysdep/autoconf.h`

Selected configuration options:

| Option | Value |
|---------|------|
| POSIX Threads | Enabled |
| Kernel MPLS Support | Enabled |
| Client Utilities | Enabled |
| Debug Build | Disabled |

Enabled routing protocols:

- Aggregator
- BFD
- Babel
- BGP
- L3VPN
- MRT
- OSPF
- PERF
- PIPE
- RADV
- RIP
- RPKI
- Static

---

# Building the Project

The project was compiled using all available CPU cores.

```bash
make -j$(nproc)
```

## Result

The project compiled successfully.

Generated executables:

- `bird`
- `birdc`
- `birdcl`

---

# Build Messages

## Git Metadata Warning

During compilation, the following message appeared:

```text
fatal: not a git repository (or any of the parent directories): .git
```

### Explanation

The source code was downloaded as a ZIP archive rather than cloned using Git.

The project Makefile attempts to retrieve Git metadata during the build process. Since the extracted archive does not contain the `.git` directory, this message is expected and does not affect compilation.

---

## Compiler Warning

The compiler also reported the following warning:

```text
warning: ignoring return value of 'write'
```

This is a compiler warning indicating that the return value of the `write()` system call is not checked.

The warning does not prevent the project from compiling successfully.

---

# Summary

The BIRD v2.17.1 source code was successfully prepared for static analysis.

Completed steps:

- Downloaded the official BIRD v2.17.1 source archive
- Extracted the project
- Generated the `configure` script using Autotools
- Successfully configured the project
- Successfully built the project
- Verified that the project is ready for static analysis using:
  - SonarQube
  - CodeQL
  - Semgrep
  - Cppcheck