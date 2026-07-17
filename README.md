# MCP Servers in Python

## Description
A Programming Learning MCP Server built with FastMCP, exposing a local programming topics dataset through MCP tools and a resource. A small LLM-based agent (Qwen3 8B via ADK + LiteLLM + Ollama) connects to the server to answer student questions using data it retrieves through the protocol — never bypassing it with direct function imports.

## MCP Architecture Summary

**What is MCP?**
The Model Context Protocol (MCP) is a standardized protocol — not a library — that defines how AI applications connect to external tools and data sources. Instead of writing a custom integration for every API or database an agent needs, developers expose those capabilities through an MCP server, and any MCP-compatible client can connect to it the same way.

**MCP Host**
The host is the overall application that manages one or more MCP clients and coordinates the interaction between the user, the AI model, and the connected servers. In this project, the host role is simplified and merged into `client/agent.py`.

**MCP Client**
The client opens and maintains a connection to a specific MCP server. Here, `client/agent.py` (via ADK's `McpToolset`) and `client/mcp_client.py` (a standalone test client) both act as clients: they decide when to call the server and consume its results.

**MCP Server**
The server is a passive program that exposes tools and resources over the MCP protocol. It doesn't decide anything on its own — it only responds to requests. `server/learning_server.py` hosts the programming topic dataset.

**Tools vs Resources**
- A **resource** is read-only data the server makes available (e.g. the full topic catalog) — the client reads it passively.
- A **tool** is an action the server exposes that the client actively calls with arguments and gets a computed result back (e.g. `search_topics("decorators")`).

**Why expose only what's necessary**
A server should only expose the capabilities it truly needs (principle of least privilege). This project's agent uses ADK's `tool_filter` to restrict itself to exactly `search_topics` and `get_topic_details`, even though the server could expose more.

## Requirements
- Python 3.10+
- [Ollama](https://ollama.com) with `qwen3:8b` pulled
- Node.js is **not** required for this project (pure Python MCP server via FastMCP)

## Setup

```bash
git clone <your-repo-url>
cd mcp-intro
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` includes: `fastmcp`, `google-adk`, `litellm`, `mcp`, `python-dotenv`.

Copy `.env.example` to `.env` if you need to override defaults:
```bash
cp .env.example .env
```

Make sure Ollama is running and `qwen3:8b` is available (`ollama serve` + `ollama pull qwen3:8b`).

## How to Run the Server

```bash
python server/learning_server.py
```

The server runs over stdio transport and stays silent while waiting for a client connection (no output is expected — this is normal, not an error). Stop it with `Ctrl+C`.

## How to Test the Server

```bash
python client/mcp_client.py
```

This connects a standalone FastMCP client to the server (auto-launched as a subprocess), and tests: listing tools, `search_topics` with a valid query, `get_topic_details` with both a valid and an invalid id, and reading the `topics://catalog` resource. See Example Output below for a sample run.

## How to Run the Agent

```bash
python client/agent.py "I want to study Python decorators. What should I review first?"
```

Requires `ollama serve` running in a separate terminal. The agent connects to the MCP server automatically (spawned as a subprocess via stdio, through ADK's `McpToolset`/`StdioConnectionParams`) and saves its response to `output/sample_agent_response.md`.

## Available Tools

| Tool | Description | Arguments | Returns |
|---|---|---|---|
| `search_topics` | Searches topics by title or key concepts (case-insensitive substring match) | `query: str` | List of matching topic objects (empty list if no match) |
| `get_topic_details` | Retrieves full details for one topic by exact id | `topic_id: str` | Full topic dict, or `{"error": "Topic not found"}` if the id doesn't exist |

## Available Resources

| Resource URI | Description | Returns |
|---|---|---|
| `topics://catalog` | Read-only catalog of all available topics | JSON string with a list of `{id, title}` for every topic in the dataset |

## Third-Party MCP Server Review

**Server**: [Filesystem MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) — official reference server maintained by the Model Context Protocol team, published on npm as `@modelcontextprotocol/server-filesystem`.

- **What it does**: exposes secure file operations (read, write, list directories, move/rename, search) to a connected AI application.
- **Local or remote**: local. Runs as a subprocess over stdio, launched via `npx` — no external network calls.
- **Tools/resources exposed**: filesystem operation tools (read file, write file, list directory, move/copy, search files, get file info).
- **Permissions/credentials required**: no API key, but requires an explicit list of **allowed directories** passed at startup; it refuses any operation outside that scope by design.
- **Risk**: since the connected LLM is non-deterministic, it could decide to delete or modify critical files — from an ambiguous instruction, a hallucination, or a prompt injection hidden in processed content. The blast radius scales directly with how broad the allowed directory scope is.
- **Safety measure**: scope the allowed directory to the exact project folder needed, never a broad parent directory like the full home folder — the same least-privilege principle applied in this project to `tool_filter`.

## Example Output

Test client (`python client/mcp_client.py`) — abbreviated:
```
Available tools: ['search_topics', 'get_topic_details']
Search result: [...{"id":"python-decorators","title":"python decorators", ...}]
Details result: {"id": "python-decorators", ...}
Invalid id result: {"error": "Topic not found"}
Catalog: [{"id": "list-comprehension", "title": "list comprehension"}, ...]
```

Agent response (`output/sample_agent_response.md`), for *"I want to study Python decorators. What should I review first?"*:
```markdown
Pour étudier les decorators en Python, commencez par réviser les bases des
fonctions et des lambda functions...

### Concepts fondamentaux
- Decorators : Fonctions qui modifient le comportement d'autres fonctions...
- Wrappers : Fonctions internes créées par les decorators...

### Erreurs courantes
- Ne pas comprendre l'ordre d'exécution des décorateurs...

### Exercice pratique
Créez un décorateur qui mesure et affiche le temps d'exécution d'une fonction...
```

## Known Limitations
- The agent sometimes invents plausible-but-unverified details despite an explicit instruction not to (`"Do not invent topic details that were not provided by the MCP server"`). In testing, it recommended reviewing "lambda functions" as a prerequisite for decorators — a topic that doesn't even exist in `data/topics.json`, and added a prerequisite (higher-order functions) not present in the (empty) `prerequisites` field of the real data. This is a known risk with local reasoning models and should be treated as a hard limitation, not an edge case.
- `data/topics.json` has empty `prerequisites` lists for all 5 topics — reducing the dataset's usefulness and likely contributing to the hallucination above (an empty field may read to the model as "missing" rather than "genuinely none").
- The test client (`client/mcp_client.py`) and the agent (`client/agent.py`) each launch their own subprocess connection to the server — there's no shared, persistent server process across multiple client runs.
- Only tested with `qwen3:8b`; behavior with larger models or other providers (Gemini, Claude, OpenAI via LiteLLM) is undocumented.

## Reflection

**1. What problem does MCP solve?**
Without MCP, every AI application that needs to talk to an external tool or data source would need a custom, one-off integration. MCP standardizes that connection — any MCP-compatible client can use any MCP-compatible server the same way, the same way HTTP standardized how browsers talk to web servers.

**2. What is the difference between an MCP tool and an MCP resource?**
A resource is read-only data the client can passively fetch (like browsing a menu) — `topics://catalog` in this project. A tool is an action the client actively invokes with arguments and gets a computed result back — `search_topics` and `get_topic_details` here. Tools compute; resources just expose.

**3. What does your MCP server expose?**
Two tools (`search_topics` for fuzzy search by title/key concepts, `get_topic_details` for an exact lookup by id) and one resource (`topics://catalog`, a lightweight id+title listing of all 5 topics), all backed by a local `data/topics.json` file.

**4. How does your agent use the MCP server?**
`client/agent.py` defines an ADK agent (Qwen3 8B via LiteLLM/Ollama) with an `McpToolset` connected to the server over stdio (the server is launched as a subprocess automatically). The toolset is restricted with `tool_filter` to only `search_topics` and `get_topic_details`. The LLM itself decides when and how to call these tools based on its instruction — the agent code never calls the underlying Python functions directly, only through the MCP protocol.

**5. What should you check before using a third-party MCP server?**
What it actually does and what tools/resources it exposes, whether it runs locally or remotely (and therefore whether your data ever leaves your machine), what credentials or permissions it demands, and — critically — how narrowly you can scope its access before running it (e.g. restricting a filesystem server to one project folder instead of the whole home directory).

**6. What limitation did you observe in your implementation?**
Even with an explicit instruction not to invent information ("Do not invent topic details that were not provided by the MCP server"), Qwen3 hallucinated a prerequisite topic ("lambda functions") that doesn't exist anywhere in the dataset. This shows that MCP's data-grounding only constrains what's *available* to the model — it doesn't guarantee the model will *stick to* that data. Deterministic validation (like the `validate_required_sections` tool from the previous project) would be a natural next addition to catch this kind of drift automatically rather than relying on the prompt alone.