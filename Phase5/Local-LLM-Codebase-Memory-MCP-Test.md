# Local LLM Integration with Codebase Memory MCP Using Ollama and Cline

## 1. Overview

This document records a test of a local LLM connected to Codebase Memory MCP through Cline in Visual Studio Code. The goal was to verify that the model could use MCP tools sequentially to find a function in an indexed C codebase, retrieve its source, and explain it based on the returned evidence.

| Component | Configuration |
|---|---|
| Operating system | Ubuntu 24.04.4 LTS |
| LLM runtime | Ollama 0.40.11 |
| Local model | Qwen3 4B (`qwen3:4b`) |
| MCP client | Cline for Visual Studio Code |
| MCP server | Codebase Memory MCP 0.12.1 |
| Repository | BIRD |
| Target function | `bgp_decode_nlri_flow4` |

Codebase Memory MCP installation and indexing are documented separately. This document focuses on Ollama, Cline configuration, and validation.

## 2. Architecture

```text
User
 |
 v
Cline (VS Code) ------> Ollama HTTP API ------> Qwen3 4B
 |
 v
Codebase Memory MCP tools
 |
 v
Indexed BIRD repository
 |
 v
Search results and source code
```

Ollama runs the model and exposes an HTTP API. Cline communicates with Ollama and invokes MCP tools. The MCP server returns information from its indexed codebase; the model does not access the graph database directly.

## 3. Installing Ollama

The official installation script and direct official download endpoint returned HTTP 403 errors. Ollama was therefore installed from the Linux AMD64 GitHub release archive.

### 3.1. Download and extract

```bash
curl -fL https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64.tar.zst \
  -o /tmp/ollama-linux-amd64.tar.zst

ls -lh /tmp/ollama-linux-amd64.tar.zst

sudo tar --zstd -xf /tmp/ollama-linux-amd64.tar.zst -C /usr
```

The download completed successfully (approximately 1.4 GB; the file was reported as 1.5 GB). The extraction command was run twice during installation.

### 3.2. Verify the installation and service status

```bash
ollama --version
systemctl status ollama --no-pager
```

The client reported version `0.40.11`, along with a warning that no Ollama instance was running. The service check returned:

```text
Unit ollama.service could not be found.
```

Thus, Ollama was run manually rather than through a configured `ollama.service` systemd unit.

## 4. Download and run Qwen3 4B

Check the local model list:

```bash
ollama list
```

Download the model:

```bash
ollama pull qwen3:4b
```

Verify that it is installed:

```bash
ollama list
```

The output listed `qwen3:4b`, ID `359d7dd4bcda`, with a size of approximately 2.5 GB. Further metadata can be inspected with:

```bash
ollama show qwen3:4b
```

Start an interactive session:

```bash
ollama run qwen3:4b
```

Ollama displayed the prompt `>>>`, where a test such as `hello` could be entered.

The local API endpoint is `http://localhost:11434`. To list locally available models through the API, run the command while the server is active:

```bash
curl http://localhost:11434/api/tags
```

## 5. Set the context length

During initial testing, the model runner was using a context size of 4096 tokens. This was checked with:

```bash
ps aux | grep '[o]llama'
```

The model runner's arguments included `-c 4096`. To test a larger context, the model was launched with:

```bash
OLLAMA_NUM_CTX=16384 ollama run qwen3:4b
```

Later, the Ollama server was started with an explicit context length:

```bash
OLLAMA_CONTEXT_LENGTH=16384 ollama serve
```

Keep the server process running while using Cline. The context available to an individual request also depends on the client settings and the size of the conversation and tool results.

## 6. Configure Cline and connect MCP

Cline was installed as a Visual Studio Code extension and configured with these Ollama settings:

| Setting | Value |
|---|---|
| API Provider | Ollama |
| Base URL | `http://localhost:11434` |
| Model | `qwen3:4b` |

Cline was connected to the existing Codebase Memory MCP executable:

```text
/home/nazanin/.local/bin/codebase-memory-mcp
```

The server used stdio transport. The Cline MCP interface showed:

| Item | Observed result |
|---|---|
| Server | `codebase-memory` |
| Tools | 17 |
| Resources | 0 |
| Prompts | 2 |

Available tools included `list_projects`, `search_graph`, `query_graph`, `trace_path`, and `get_code_snippet`. These results confirmed that Cline discovered the configured server and its tools.

## 7. Test 1: List indexed projects

The first test asked Cline to list the indexed projects using the `codebase-memory` MCP server. Cline called `list_projects`, which returned:

```text
projects: 1 (cols: name root_path branch)
 home-nazanin-Projects-bird-2.17-2-.1 "/home/nazanin/Projects/bird-2.17 (2).1" -
total: 1
returned: 1
has_more: false
```

Cline reported the project name `home-nazanin-Projects-bird-2.17-2-.1` and root path `/home/nazanin/Projects/bird-2.17 (2).1`. This confirmed that Cline could invoke an MCP tool and use its response.

## 8. Test 2: Find a function and retrieve its source

### 8.1. Test prompt

The following prompt was submitted to Cline:

```text
Use the `codebase-memory` MCP server to inspect the function `bgp_decode_nlri_flow4` in the indexed BIRD project.

Follow these steps in order:
1. Call `search_graph` to find the function named `bgp_decode_nlri_flow4`. Use the indexed project name `home-nazanin-Projects-bird-2.17-2-.1`.
2. From the search result, obtain the function's exact `qualified_name`.
3. Call `get_code_snippet` using that exact `qualified_name` and the same project name. Request the full source if possible.
4. Based only on the tool results, report:
   - The exact function name
   - The source file and line range
   - A short explanation of what the function does

You must execute both tools in sequence. Do not invent results or answer from prior knowledge. Keep the final response concise.
```

### 8.2. First call: `search_graph`

Cline called `search_graph` with:

```json
{
  "project": "home-nazanin-Projects-bird-2.17-2-.1",
  "query": "bgp_decode_nlri_flow4"
}
```

It returned one result:

```text
results: 1 (cols: qn label file lines rank)
home-nazanin-Projects-bird-2.17-2-.1.proto.bgp.packets.bgp_decode_nlri_flow4 Function proto/bgp/packets.c 2066-2124 -53.74
total: 1
total_relation: eq
search_mode: bm25
returned: 1
has_more: false
truncated: false
```

The exact qualified name was:

```text
home-nazanin-Projects-bird-2.17-2-.1.proto.bgp.packets.bgp_decode_nlri_flow4
```

The result identified the symbol as a function in `proto/bgp/packets.c`, lines 2066–2124.

### 8.3. Second call: `get_code_snippet`

Cline then called `get_code_snippet` using the qualified name returned by the first tool:

```json
{
  "qualified_name": "home-nazanin-Projects-bird-2.17-2-.1.proto.bgp.packets.bgp_decode_nlri_flow4",
  "project": "home-nazanin-Projects-bird-2.17-2-.1",
  "max_lines": 500
}
```

The response metadata was:

```text
name: bgp_decode_nlri_flow4
qualified_name: home-nazanin-Projects-bird-2.17-2-.1.proto.bgp.packets.bgp_decode_nlri_flow4
label: Function
file_path: "/home/nazanin/Projects/bird-2.17 (2).1/proto/bgp/packets.c"
start_line: 2066
end_line: 2124
source_mode: full
callers: 0
callees: 11
```

The tool returned the full source of the function. Its main operations, as shown in the returned source, were to read an optional Add-Path identifier, parse flow lengths, validate the flow data, extract a destination IPv4 prefix when present, construct a flow network address, optionally apply validation associated with RFC 8955, and update routing information.

The response also warned that some regions of `proto/bgp/packets.c` had not been fully parsed during graph indexing. This may make graph relationships incomplete; the returned source was used as the primary evidence for the explanation.

## 9. Verify the result directly through the CLI

The same MCP tools were called directly from the terminal to compare their results with Cline. These commands assume the MCP CLI is already installed and configured.

### 9.1. Inspect and run `search_graph`

```bash
codebase-memory-mcp cli search_graph --help
```

Relevant options included `--project`, `--query`, and `--format`.

```bash
codebase-memory-mcp cli search_graph \
  --project "home-nazanin-Projects-bird-2.17-2-.1" \
  --query "bgp_decode_nlri_flow4" \
  --format json
```

The JSON response contained one result with the same qualified name, file `proto/bgp/packets.c`, and line range `2066-2124`.

### 9.2. Inspect and run `get_code_snippet`

```bash
codebase-memory-mcp cli get_code_snippet --help
```

Relevant options included `--qualified-name`, `--project`, `--source-mode`, `--max-lines`, and `--format`.

```bash
codebase-memory-mcp cli get_code_snippet \
  --project "home-nazanin-Projects-bird-2.17-2-.1" \
  --qualified-name "home-nazanin-Projects-bird-2.17-2-.1.proto.bgp.packets.bgp_decode_nlri_flow4" \
  --source-mode full \
  --format json
```

The direct CLI response confirmed the function name, qualified name, source file, line range, and `source_mode: full`. The returned source matched the source retrieved through Cline.

## 10. Results

The Cline trace showed this sequence:

1. `search_graph` found the target function.
2. Cline extracted the exact `qualified_name` from the result.
3. `get_code_snippet` was called with that name and the same project identifier.
4. The full source and metadata were returned.
5. Cline produced an explanation consistent with the source.
6. Direct CLI execution independently confirmed the result.

| Verification item | Result |
|---|---|
| Function | `bgp_decode_nlri_flow4` |
| Source file | `proto/bgp/packets.c` |
| Lines | 2066–2124 |
| Source retrieval | Full source returned |
| Sequential tool calls | Successful |
| CLI comparison | Matched Cline results |

This test demonstrated a working local-model/MCP integration and one sequential two-tool workflow. It does not prove that the model will always call tools correctly or discover software vulnerabilities.

## 11. Limitations

- **Performance:** Long tool-oriented requests sometimes took considerable time. The test confirms functional integration, not optimal latency.
- **Context:** The server was run with a 16,384-token context. The effective context also depends on client settings and the size of conversation and tool results.
- **Graph indexing:** Some regions of `proto/bgp/packets.c` were not fully parsed for graph relationships, so graph-derived results may be incomplete.
- **Scope:** Testing covered one repository, one function, and one two-tool workflow. More tests are needed for ambiguous symbols, complex queries, incomplete indexing, and vulnerability analysis.

## 12. Initial attempt with OpenCode

An earlier attempt used OpenCode with the local Ollama model. Although the MCP server appeared connected, requests involving tool execution sometimes remained in prolonged reasoning and did not produce a useful final response within a reasonable time. Testing was continued with Cline, which completed both tests described above. This records the observed outcome and does not imply that OpenCode is generally incompatible with Ollama or Codebase Memory MCP.

## 13. Conclusion

The experiment demonstrated an end-to-end workflow in which Cline used a locally hosted Qwen3 4B model through Ollama to search for `bgp_decode_nlri_flow4`, pass the returned qualified name to a second MCP tool, retrieve the function source, and explain it. Direct CLI calls independently confirmed the function metadata and source location.

The result provides a working baseline for further code-understanding experiments using a local LLM and an MCP-based code context server.