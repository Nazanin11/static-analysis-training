# Graphify MCP – Setup and Test

## 1. Installation

Graphify was installed using `uv` with MCP support:

```bash
uv tool install "graphifyy[mcp]"
```

Verify the installation and check the available commands:

```bash
graphify --help
graphify-mcp --help
```

Check the MCP executable path:

```bash
which graphify-mcp
```

Installed version: `0.9.101`

## 2. Indexing the BIRD Repository

Navigate to the BIRD repository:

```bash
cd ~/Projects/bird-2.17\ \(2\).1
```

Run code-only extraction to build the initial graph without requiring an LLM API key:

```bash
graphify extract . --code-only
```

This step performs AST-based code extraction and generates the graph files in:

```text
graphify-out/
```

## 3. Generating the Graph Visualization

Run the clustering process:

```bash
graphify cluster-only .
```

This command clusters the extracted graph and generates the following files:

- `graph.json`: Main graph data.
- `graph.html`: Interactive graph visualization.
- `GRAPH_REPORT.md`: Graph analysis report.

Since the BIRD graph contains more than 5,000 nodes, Graphify automatically generates an aggregated community view.

Open the visualization:

```bash
xdg-open graphify-out/graph.html
```

Check the generated files:

```bash
ls -lh graphify-out/
```

## 4. Connecting Graphify MCP to Cline

The Graphify MCP executable is located at:

```text
/home/nazanin/.local/bin/graphify-mcp
```

Add the following server configuration to Cline's `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "codebase-memory": {
      "command": "/home/nazanin/.local/bin/codebase-memory-mcp",
      "args": []
    },
    "graphify": {
      "command": "/home/nazanin/.local/bin/graphify-mcp",
      "args": [
        "/home/nazanin/Projects/bird-2.17 (2).1/graphify-out/graph.json"
      ]
    }
  }
}
```

The existing Codebase Memory MCP configuration is preserved, allowing both MCP servers to run simultaneously.

After saving the configuration, check the MCP server status in Cline.

Graphify MCP exposed 10 tools and 6 resources.

**Tools:**

- `query_graph`
- `get_node`
- `get_neighbors`
- `get_community`
- `god_nodes`
- `graph_stats`
- `shortest_path`
- `list_prs`
- `get_pr_impact`
- `triage_prs`

**Resources:**

- `graphify://report`
- `graphify://stats`
- `graphify://god-nodes`
- `graphify://surprises`
- `graphify://audit`
- `graphify://questions`

## 5. Graphify MCP Experiments Using Cline and Qwen3:4B

After connecting Graphify MCP to Cline, several experiments were performed using the local `Qwen3:4B` model through Ollama.

The experiments focused on testing Graphify's graph-querying capabilities and verifying whether the model could correctly invoke the MCP tools and interpret their results.

All experiments used the following BIRD repository:

```text
/home/nazanin/Projects/bird-2.17 (2).1
```

### 5.1. Experiment 1 – Finding the Shortest Path Between Two Functions

**Objective:**

Test the `shortest_path` tool to determine whether Graphify can find the relationship and shortest connection path between two specified functions in the BIRD codebase.

**Prompt:**

```text
You are testing Graphify MCP on the BIRD 2.17.1 repository.

Project path:
/home/nazanin/Projects/bird-2.17 (2).1

Use ONLY the shortest_path tool with these parameters:

- source: bgp_decode_nlri_flow4
- target: bgp_apply_flow_validation
- max_hops: 5
- project_path: /home/nazanin/Projects/bird-2.17 (2).1

Do not read MCP resources.
Do not read graph.json directly.
Do not use any other Graphify tools.
Do not reuse results from previous tasks.

Execute the tool and report:
1. Whether a path was found.
2. The complete path and relationship types.
3. The confidence classification of the path.

Use only the actual tool output. Do not invent missing relationships.
```

**Tool Called:**

`shortest_path`

**Tool Arguments:**

```json
{
  "target": "bgp_apply_flow_validation",
  "max_hops": 5,
  "project_path": "/home/nazanin/Projects/bird-2.17 (2).1",
  "source": "bgp_decode_nlri_flow4"
}
```

**Graphify Tool Output:**

```text
Shortest path (1 hops):
 bgp_decode_nlri_flow4() --calls [EXTRACTED]--> bgp_apply_flow_validation()
Path confidence: EXTRACTED (weakest hop 1: calls)
```

**Model Output:**

```text
A path was found between the two functions.

Shortest path (1 hop):

bgp_decode_nlri_flow4()
    --calls [EXTRACTED]-->
bgp_apply_flow_validation()

Path confidence: EXTRACTED

The relationship between the two functions is classified as an extracted
relationship, and only one hop is required to connect them.
```

**Result and Analysis:**

- Graphify successfully found a path between the two specified functions.
- The path contains only one edge.
- The relationship is classified as `calls`.
- The confidence classification is `EXTRACTED`.
- The model correctly interpreted the returned path and its relationship type.

This experiment demonstrates that Graphify can retrieve a direct relationship between two functions using the `shortest_path` tool.

### 5.2. Experiment 2 – Retrieving Graph Statistics and Identifying Highly Connected Nodes

**Objective:**

Test the `graph_stats` and `god_nodes` tools to retrieve general information about the generated graph and identify its most highly connected nodes.

This experiment also checks whether the model can invoke multiple Graphify tools in one task and combine their results.

**Prompt:**

```text
You are testing Graphify MCP on the BIRD 2.17.1 repository.

Project path:
/home/nazanin/Projects/bird-2.17 (2).1

Execute the following Graphify tools in order:

1. Call graph_stats to retrieve:
   - Total number of nodes
   - Total number of edges
   - Number of communities
   - Relationship confidence breakdown

2. Call god_nodes with top_n = 5 to retrieve the five most connected nodes.

For both tools, use this project path:
/home/nazanin/Projects/bird-2.17 (2).1

Important restrictions:
- Execute both tools in this task.
- Do not read MCP resources.
- Do not read graph.json directly.
- Do not use any other Graphify tools.
- Do not reuse results from previous tasks.

After executing both tools, present the actual results in a structured format.
Briefly explain what the graph statistics and highly connected nodes represent.

Do not invent or infer information that is not present in the tool outputs.
```

**Tools Called:**

- `graph_stats`
- `god_nodes`

**Tool Arguments:**

`graph_stats`:

```json
{
  "project_path": "/home/nazanin/Projects/bird-2.17 (2).1"
}
```

`god_nodes`:

```json
{
  "project_path": "/home/nazanin/Projects/bird-2.17 (2).1",
  "top_n": 5
}
```

**Graphify Tool Output – graph_stats:**

```text
Nodes: 5541
Edges: 15840
Communities: 228
EXTRACTED: 73%
INFERRED: 27%
AMBIGUOUS: 0%
```

**Graphify Tool Output – god_nodes:**

```text
God nodes (most connected):
 1. sock - 168 edges
 2. ip_addr - 140 edges
 3. current_time() - 111 edges
 4. add_tail() - 87 edges
 5. bgp_config - 84 edges
```

**Model Output:**

```text
Graph Statistics:

- Total nodes: 5,541
- Total edges: 15,840
- Communities: 228

Relationship confidence breakdown:
- EXTRACTED: 73%
- INFERRED: 27%
- AMBIGUOUS: 0%

Top 5 Most Connected Nodes:

| Rank | Node          | Number of Edges |
|------|---------------|-----------------|
| 1    | sock          | 168             |
| 2    | ip_addr       | 140             |
| 3    | current_time()| 111             |
| 4    | add_tail()    | 87              |
| 5    | bgp_config    | 84              |

The graph_stats tool provides an overview of the graph structure,
including the number of nodes, edges, communities, and relationship
confidence classifications.

The god_nodes tool identifies nodes with the highest number of
connections in the graph.
```

**Result and Analysis:**

- Both requested tools were successfully invoked.
- Graphify reported 5,541 nodes and 15,840 edges.
- The graph contains 228 communities.
- 73% of the relationships are classified as `EXTRACTED`, while 27% are classified as `INFERRED`.
- No relationships were classified as `AMBIGUOUS`.
- The `god_nodes` tool successfully returned the five most connected nodes.

The model correctly transferred the numerical results into its response and presented them in a structured table.

It is important to note that a high number of connections does not necessarily indicate that a node is vulnerable or more important from a security perspective. It only indicates that the node has many relationships in the graph.

Also, the `EXTRACTED` and `INFERRED` labels describe Graphify's relationship classifications. They should not be interpreted as proof that every relationship is semantically correct.

## 6. Summary of Experiments

The following table summarizes the completed experiments:

| Experiment | Graphify Tool(s) | Purpose | Result |
|---|---|---|---|
| Shortest Path | `shortest_path` | Find the connection between two functions | Successful |
| Graph Statistics | `graph_stats` | Retrieve graph structure and relationship statistics | Successful |
| Highly Connected Nodes | `god_nodes` | Identify the five most connected nodes | Successful |

### Overall Observations

The experiments confirmed that:

1. Graphify MCP was successfully connected to Cline and was accessible to the local Qwen3:4B model.
2. The model successfully invoked individual Graphify tools and interpreted their outputs.
3. The `shortest_path` tool retrieved a direct relationship between two BIRD functions.
4. The `graph_stats` tool provided an overview of the generated code graph.
5. The `god_nodes` tool identified the most highly connected nodes.
6. Explicitly limiting each experiment to the required tools helped keep the tests focused and avoided unnecessary resource loading.

These experiments provide an initial evaluation of Graphify MCP's ability to expose code-graph information to an LLM. Further experiments can investigate node details, direct neighbors, community structure, and graph-based code exploration.