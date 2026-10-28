# Codebase Memory MCP: Installation, Graph Generation, and Visualization

## 1. Overview

Codebase Memory MCP is a tool that analyzes a software repository and builds a graph representing its code structure and relationships. The graph can be queried to explore functions, files, and relationships between code elements.

This document describes the installation and setup of Codebase Memory MCP, indexing the BIRD repository, persisting the generated graph, and viewing the results through the graphical interface.

## 2. Environment and Repository

The following environment was used:

- **Operating System:** Ubuntu 24.04 LTS
- **Repository:** BIRD 2.17.1
- **Repository Path:** `/home/nazanin/Projects/bird-2.17 (2).1`
- **Codebase Memory MCP Version:** 0.12.1

## 3. Installation

The installation script was executed from the repository directory. Before running the installer, the permissions of the local binary directory were corrected.

```bash
chmod 755 ~/.local/bin
```
Download the installation script:
```bash
cd ~/Projects
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh -o install-codebase-memory.sh
```
Run the installation script:

```bash
bash ~/Projects/'bird-2.17 (2).1'/install-codebase-memory.sh --skip-config
```

Verify the installation:

```bash
codebase-memory-mcp --version
```

Display the available command-line options:

```bash
codebase-memory-mcp --help
```

## 4. Indexing the BIRD Repository

Indexing analyzes the repository and creates a graph of its code structure and relationships.

Run the indexing command with progress reporting and persistence enabled:

```bash
codebase-memory-mcp cli --progress index_repository \
  --repo-path "/home/nazanin/Projects/bird-2.17 (2).1" \
  --persistence true
```

The `--repo-path` argument specifies the repository to analyze. The persistence option enables saving the generated graph so that it can be reused rather than existing only as temporary in-memory data.

## 5. Generated Output and Persistence

The persistent graph data is stored in the following directory inside the repository:

```text
.codebase-memory/
├── graph.db.zst
└── artifact.json
```

The main output is:

```text
.codebase-memory/graph.db.zst
```

This file contains the persisted graph database. The `artifact.json` file stores additional artifact information.

To inspect the generated files, run:

```bash
ls -lh "/home/nazanin/Projects/bird-2.17 (2).1/.codebase-memory/"
```

Execution output can also be redirected to a log file when running the indexing command:

```bash
codebase-memory-mcp cli --progress index_repository \
  --repo-path "/home/nazanin/Projects/bird-2.17 (2).1" \
  --persistence true \
  2>&1 | tee bird-graph-export.log
```

The log records the command's execution output. It is separate from the persisted graph database.

**Note:** `graph.db.zst` is the persisted graph database, not an image of the graph. The log file is also not a graph export.

## 6. Viewing Results Through the Graphical Interface

Codebase Memory MCP provides a graphical interface that can be launched with the `--ui` option.

Start the interface on port 9749:

```bash
codebase-memory-mcp --ui=true --port=9749
```

Once the interface starts, open the following address in a web browser:

```text
http://localhost:9749
```

The graphical interface can be used to explore the indexed project and inspect the available graph-related views and information.

The interface includes areas for exploring the codebase, examining its architecture, and navigating graph-related information. The exact information available depends on the indexed repository and the selected view.

## 7. Querying Graph Information from the Command Line

Graph information can also be retrieved through the CLI.

For example, list the indexed projects:

```bash
codebase-memory-mcp cli list_projects
```

Search for a code element in the graph:

```bash
codebase-memory-mcp cli search_graph --help
```

Inspect the available graph query options:

```bash
codebase-memory-mcp cli query_graph --help
```

The help commands show the arguments supported by the installed version. Once the required arguments are specified, graph query results can be retrieved from the command line.

For commands that support JSON output, JSON formatting can be used to obtain structured results for further processing:

```text
--format json
```

The option should be used with commands that support it.

## 8. Summary

The workflow described in this document covers installing Codebase Memory MCP, indexing the BIRD repository, persisting the generated graph, and accessing graph information through the command line and graphical interface.

The persisted graph database provides a reusable representation of the repository's structure and relationships. The graphical interface provides a more convenient way to explore the indexed information, while CLI queries support structured retrieval and further processing.