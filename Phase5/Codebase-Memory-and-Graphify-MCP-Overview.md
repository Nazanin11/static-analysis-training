# Codebase Memory MCP – Tools Overview

Codebase Memory MCP provides 17 tools for indexing repositories, searching code, retrieving source code, analyzing relationships between code components, and examining project architecture and changes.

The following sections briefly describe the purpose of each tool.

## 1. Project Management and Indexing

### 1. `index_repository`
Indexes a source code repository by analyzing its structure, symbols, and relationships. The extracted information is stored in a graph that can later be queried by other tools. Different indexing modes are available depending on the desired level of analysis.

### 2. `list_projects`
Lists the repositories that have already been indexed by Codebase Memory. It can provide project names, root paths, and optional statistics about the indexed graph.

### 3. `delete_project`
Removes an indexed project and its associated graph data from Codebase Memory.

### 4. `index_status`
Checks the indexing status of a project. It can report information such as project readiness, node and edge counts, repository root, and detected coverage gaps.

### 5. `check_index_coverage`
Checks the indexing coverage of specific files, paths, or project scopes. It helps identify areas that may be missing from the index or require further inspection.

## 2. Code Search and Retrieval

### 6. `search_graph`
Searches the project graph for code symbols such as functions, classes, and other program elements. It can return information including symbol names, qualified names, file paths, line numbers, and graph relationships.

### 7. `search_code`
Searches the indexed source code for a specific text pattern or expression. It is useful for finding occurrences of function names, variables, keywords, or code fragments across project files.

### 8. `get_code_snippet`
Retrieves the source code of a specific symbol, such as a function or class. Depending on the requested options, it can also provide additional information, including file location, line numbers, and neighboring code elements.

### 9. `get_file_outline`
Provides a structural overview of a specific source file. It lists declarations such as functions, classes, and structures in their original source-code order.

## 3. Graph and Relationship Analysis

### 10. `trace_path`
Traces relationships between code components through the project graph. For example, it can identify the functions called by a specific function (callees) and the functions that call it (callers). Depending on the selected mode, it can also investigate data-flow paths and cross-service relationships.

### 11. `query_graph`
Executes custom read-only Cypher queries against the project graph. It can be used to retrieve more complex information, such as multi-step relationships, graph statistics, and connections between different project components.

### 12. `get_graph_schema`
Provides information about the graph structure, including available node labels, relationship types, and, in diagnostic mode, queryable properties. It helps users understand how project information is represented in the graph.

### 13. `get_architecture`
Provides a static overview of the project's architecture. It can retrieve information about programming languages, packages, entry points, and the overall structure of the system.

## 4. Change Analysis

### 14. `detect_changes`
Analyzes Git changes and identifies the files and code components affected by them. It can also examine relationships between changed components and other parts of the project to help determine the potential impact of modifications.

### 15. `compare_graphs`
Compares two indexed snapshots of a project. It identifies nodes and relationships that have been added or removed between the two versions.

## 5. Architecture Documentation and Runtime Information

### 16. `manage_adr`
Manages Architecture Decision Records (ADRs). It supports listing document sections, reading existing documents, replacing the entire document, and updating specific sections.

### 17. `ingest_traces`
Receives and stores observed runtime call traces in the project graph. This information helps distinguish relationships that have actually been observed during program execution from relationships that are only identified through static analysis.

## Conclusion

Codebase Memory MCP provides a set of tools that allow language models to interact with the structural and textual information of a software repository.

These tools cover several areas, including repository indexing, code search, source-code retrieval, relationship analysis, architecture exploration, and change detection.

By combining these capabilities, a language model can retrieve relevant information from the codebase in a targeted way instead of receiving the entire source code for every request.

# Graphify MCP – Tools and Resources Overview

Graphify MCP provides 10 tools and 6 resources for exploring and analyzing a codebase represented as a graph.

Its tools support graph queries, node inspection, relationship exploration, community analysis, and GitHub pull request analysis. Its resources expose predefined graph reports and summaries that can be retrieved by compatible MCP clients.

## 1. Graph Query and Exploration

### 1. `query_graph`

Searches the code graph using a natural-language question or keywords. It explores related nodes and relationships using graph traversal methods such as BFS or DFS. Options such as traversal depth, token budget, and context filters can control the amount and type of returned information.

### 2. `get_node`

Retrieves detailed information about a specific node in the graph using its label or identifier. It helps inspect individual code entities and their associated properties.

### 3. `get_neighbors`

Retrieves the nodes directly connected to a specified node, along with their relationship details. It is useful for examining the immediate dependencies and connections of a function or other code entity.

### 4. `get_community`

Retrieves the nodes belonging to a specific graph community. It helps explore groups of code entities that have been clustered based on their graph relationships.

## 2. Graph Structure and Relationship Analysis

### 5. `god_nodes`

Identifies the most highly connected nodes in the graph. These nodes have a large number of relationships and may represent important connection points within the codebase.

### 6. `graph_stats`

Provides an overview of the graph structure, including the total number of nodes, edges, communities, and the distribution of relationship confidence classifications.

### 7. `shortest_path`

Finds the shortest relationship path between two specified nodes in the graph. It can reveal how two code components are connected and report the relationship types and confidence classifications along the path.

## 3. Pull Request Analysis

### 8. `list_prs`

Lists available GitHub pull requests for a repository. It provides information that can be used to identify and inspect proposed code changes.

### 9. `get_pr_impact`

Analyzes the potential impact of a specified pull request by examining the affected code and its relationships in the graph.

### 10. `triage_prs`

Performs triage of pull requests using graph-based information to help identify and prioritize changes that may require further review.

## 4. Graphify MCP Resources

In addition to its 10 tools, Graphify MCP exposes 6 resources. Unlike tools, which perform operations when called, resources provide predefined information that an MCP client can retrieve using their resource URIs.

### 1. `graphify://report`

Provides the complete graph analysis report (`GRAPH_REPORT.md`). It contains a broader overview of the generated graph and its analysis results.

### 2. `graphify://stats`

Provides graph statistics, including the number of nodes, edges, communities, and relationship confidence classifications.

### 3. `graphify://god-nodes`

Provides a list of the most highly connected nodes in the graph.

### 4. `graphify://surprises`

Provides unusual or unexpected connections between different graph communities. It can help identify relationships that may not be obvious from the code's directory structure.

### 5. `graphify://audit`

Provides an overview of relationship classifications, distinguishing between `EXTRACTED`, `INFERRED`, and `AMBIGUOUS` relationships.

### 6. `graphify://questions`

Provides suggested questions that can be used to explore the indexed codebase through graph queries.

## Conclusion

Graphify MCP provides graph-oriented tools and resources for exploring the relationships and structure of a software repository.

Its tools support targeted graph queries, node inspection, community exploration, relationship analysis, and pull request review. Its resources provide predefined reports and summaries that can be accessed by compatible MCP clients.

By exposing code relationships through a graph, Graphify MCP allows language models to investigate connections between code components without having to manually inspect the entire repository.