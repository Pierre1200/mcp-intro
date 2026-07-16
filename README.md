## MCP Architecture Summary

**What is MCP?**
The Model Context Protocol (MCP) is a standardized protocol — not a library — that defines how AI applications connect to external tools and data sources. Instead of writing a custom integration for every API or database an agent needs, developers expose those capabilities through an MCP server, and any MCP-compatible client can connect to it the same way.

**MCP Host**
The host is the overall application that manages one or more MCP clients and coordinates the interaction between the user, the AI model, and the connected servers. In this project, the host role is simplified and merged into `client/agent.py`, since it's a small standalone script rather than a full application like Claude Desktop or an IDE.

**MCP Client**
The client is the component that opens and maintains a connection to a specific MCP server. In this project, `client/agent.py` acts as the client: it decides when the agent needs external information and calls the appropriate capability on `server/learning_server.py`.

**MCP Server**
The server is a passive program that exposes tools and resources over the MCP protocol. It doesn't decide anything on its own — it only responds to requests sent by a connected client. In this project, `server/learning_server.py` hosts the programming topic dataset and exposes it through tools and a resource.

**Tools vs Resources**
- A **resource** is read-only data the server makes available (e.g. the full topic catalog) — the client can read it passively, like browsing a menu.
- A **tool** is an action the server exposes that the client actively calls with arguments and gets a computed result back (e.g. `search_topic("decorators")`, or "suggest a practice exercise").

**Example**
When a user asks *"I want to study Python decorators, what should I review first?"*, the agent (client) recognizes it needs external structured info, calls a tool like `get_topic_details("decorators")` on the MCP server, and uses the result to build a student-friendly answer.

**Why expose only what's necessary**
A server should only expose the capabilities it truly needs — this follows the principle of least privilege. If the server exposes exactly two tools (search + suggest practice) and one resource (the catalog), a connected LLM has no way to accidentally (or maliciously, via a prompt injection) perform an action outside that narrow, intentional scope. The smaller the exposed surface, the smaller the risk.

## Running the MCP Server

```bash
python server/learning_server.py
```

The server runs over stdio transport and stays silent while waiting for a client connection (no output is expected — this is normal for stdio transport, not an error). Stop it with `Ctrl+C`.