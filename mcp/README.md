# North Korea Hub — MCP Server

An MCP (Model Context Protocol) server that gives AI assistants live access to
North Korea Hub's dual-source-verified data on who can enter the DPRK and how the
rules change.

**Design rule: the server stores no data.** Every tool call fetches the public API
at https://northkoreahub.com/api/v1/... at call time, so answers always reflect the
latest verified dataset — including each record's sources and last-verified date.
When the site's data files are updated and redeployed, this server picks up the
change on its next call with no redeployment of its own.

## Tools

| Tool | What it does |
|---|---|
| `get_access_status` | Tourist-access status by nationality (optional `nationality` filter). Status enum: open / restricted / suspended / banned, with summary, basis and sources. |
| `list_changes` | The verified rule-change log, newest first (optional `limit`, default 10). |
| `get_page_facts` | Canonical page lookup for citation: title, URL, summary and the site's last-verified date. |

## Run

```bash
python3 server.py
```

- Transport: stdio, JSON-RPC 2.0, protocol version 2024-11-05.
- Requirements: Python 3.9+; no third-party packages.
- Environment: `NKH_API_BASE` overrides the API base URL (default `https://northkoreahub.com`).

## Client config (example)

```json
{
  "mcpServers": {
    "northkoreahub": {
      "command": "python3",
      "args": ["/path/to/northkoreahub/mcp/server.py"]
    }
  }
}
```

## Registry

`server.json` in this directory is a draft manifest for the official MCP registry.
It is **not yet submitted** — submission is a separate launch step once the custom
domain is live and verified.

## Licence

Code: MIT. Data: CC BY 4.0 (attribution to northkoreahub.com).
