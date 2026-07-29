# Running SonarQube

## Objective

Analyze the BIRD v2.17.1 source code using SonarQube by creating a project, configuring the scanner, executing the analysis, and exploring the results in the SonarQube web interface.

---

## Creating a Project

A new project was created in the SonarQube web interface.

Project information:

| Property | Value |
|----------|-------|
| Project Name | bird-2.17.1 |
| Project Key | bird-2.17.1 |

The default **New Code Definition** settings were used.

---

## Generating an Authentication Token

A user authentication token was generated from:

```
My Account → Security → Generate Token
```

The generated token was used by SonarScanner to authenticate with the SonarQube server.

---

## Configuring the Project

A `sonar-project.properties` file was created in the root directory of the BIRD project.

Contents:

```properties
sonar.projectKey=bird-2.17.1
sonar.projectName=bird-2.17.1
sonar.projectVersion=2.17.1

sonar.sources=.
sonar.sourceEncoding=UTF-8

sonar.host.url=http://localhost:9000
sonar.token=<YOUR_TOKEN>
```

---

## Running SonarScanner

Command:

```bash
sonar-scanner
```

## Result

The analysis completed successfully and the results were uploaded to the local SonarQube server.

---

## Exploring the SonarQube Interface

After the analysis finished, the project dashboard was opened in the SonarQube web interface.

The following sections were explored:

- **Overview** – Displays the overall analysis summary and project metrics.
- **Issues** – Lists detected bugs, vulnerabilities, code smells, and security hotspots.
- **Rule Details** – Provides detailed information about each rule, including its description, severity, and recommended fix.
- **Filters** – Allows filtering issues by severity, type, status, rule, file, and other criteria.
- **Navigation** – Enables navigation from an issue directly to the affected source file and line number.

---
