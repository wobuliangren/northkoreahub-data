# North Korea Hub — Open Dataset & MCP Server

**Who can enter North Korea, and how the rules change — as data.**

This repository is the public dataset mirror of
**[northkoreahub.com](https://northkoreahub.com)** — a dual-source-verified
information portal tracking DPRK (North Korea) tourist-access rules: who may
enter, on what basis, and every verified rule change since 2017.

Every record is checked against at least two independent sources before
publication, preferring primary/official sources (e.g. the US Federal
Register, UK FCDO, KOTRA statistics) and the specialist tour operators who hold
DPRK relationships. Claims that cannot be dual-verified are excluded. Full
method: https://northkoreahub.com/about/method/

## Data

| File | Contents |
|---|---|
| [`data/access.json`](data/access.json) | Tourist-access status by nationality (status enum: open / restricted / suspended / banned), summary, legal/operational basis, sources, per-record last-verified date. |
| [`data/access-by-nationality.csv`](data/access-by-nationality.csv) | The same access data, flattened for spreadsheets. |
| [`data/changes.json`](data/changes.json) | The verified rule-change log, 2017–2026 (US passport ban, Rason reopening, Wonsan-Kalma, the 2026 transport and bridge openings). |
| [`data/changes.csv`](data/changes.csv) | The same change log, flattened. |

This repository is a **snapshot mirror**. The live API is canonical and always
current; if this snapshot and the API ever disagree, the API wins.

## Live API (always current)

- https://northkoreahub.com/api/v1/access.json
- https://northkoreahub.com/api/v1/changes.json
- https://northkoreahub.com/llms.txt

## MCP server

[`mcp/`](mcp/) contains a zero-dependency Model Context Protocol server
(`mcp/server.py`, Python 3.9+, stdio) that exposes this dataset to AI
assistants. It stores no data — every tool call fetches the live API above, so
answers always carry the latest verified data and last-verified dates. See
[`mcp/README.md`](mcp/README.md) for tools and client configuration, and
[`mcp/server.json`](mcp/server.json) for the MCP registry manifest
(`io.github.wobuliangren/northkoreahub`).

## Licence

- **Data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)** — reuse
  freely with attribution to northkoreahub.com and a link back.
- **Code (`mcp/server.py`): MIT.**

## Citation

North Korea Hub. "DPRK Access by Nationality & Rule Change Log."
https://northkoreahub.com — dataset last verified 2026-11-23 (each record
carries its own last-verified date; see the data files).
