#!/usr/bin/env python3
"""North Korea Hub MCP server.

Exposes the site's dual-source-verified DPRK access data as MCP tools.
The server bundles NO data: every tool call fetches the live public API at
https://northkoreahub.com/api/v1/... so answers always reflect the latest
verified dataset, including each record's last-verified date.

Transport: stdio (JSON-RPC 2.0), protocol version 2024-11-05.
Requires: Python 3.9+, no third-party packages.

Run:  python3 server.py
Env:  NKH_API_BASE  override API base URL (default https://northkoreahub.com)
"""
import json
import os
import sys
import urllib.request

API_BASE = os.environ.get("NKH_API_BASE", "https://northkoreahub.com").rstrip("/")
TIMEOUT = 15

PAGES = {
    "home": ("Status dashboard", "/", "Who can visit North Korea now, by nationality."),
    "visit": ("Visit hub", "/visit/", "Travel rules overview and routing to all visit topics."),
    "who-can-go": ("Who can go", "/visit/who-can-go/", "Access status by nationality, explained."),
    "visa": ("The paper visa", "/visit/visa/", "How the DPRK tourist visa works: separate paper card, no passport stamp except in Rason."),
    "us-citizens": ("US citizens", "/visit/us-citizens/", "US passport restriction to 31 Aug 2027, special validation categories, penalties."),
    "money-phones-photos": ("Money, phones, photos", "/visit/money-phones-photos/", "In-country rules: foreign cash only, phone registration, photo permissions."),
    "routes-in": ("Routes in", "/visit/routes-in/", "Flights and trains into the DPRK in 2026."),
    "wonsan-kalma": ("Wonsan-Kalma", "/visit/wonsan-kalma/", "Resort status: opened Jul 2025, foreigners suspended, Russians excepted."),
    "rason": ("Rason", "/visit/rason/", "The Feb-Mar 2025 reopening record."),
    "tours": ("Tour operators", "/tours/", "Koryo, YPT, Uri, KTG, Korea Konsult compared."),
    "business": ("Business", "/business/", "Foreign-investment framework vs the UN sanctions prohibition."),
    "special-zones": ("Special economic zones", "/business/special-zones/", "Rason, Kaesong, Sinuiju and other zones, status by zone."),
    "trade": ("Trade", "/trade/", "Border crossings, the 2026 bridges, China's 98.2% trade share."),
    "updates": ("Change log", "/updates/", "Every verified rule change, 2017-2026."),
    "method": ("Method", "/about/method/", "How every claim is dual-source verified."),
}

TOOLS = [
    {
        "name": "get_access_status",
        "description": "Get the current DPRK tourist-access status. Optionally filter by nationality (e.g. 'Russia', 'United States'). Data is fetched live from northkoreahub.com and includes the status, summary, basis, sources and last-verified date for each nationality.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "nationality": {"type": "string", "description": "Optional nationality to filter by (case-insensitive substring match)."}
            },
        },
    },
    {
        "name": "list_changes",
        "description": "List verified North Korea access rule changes (newest first), fetched live from northkoreahub.com. Optionally limit the number of entries.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Maximum number of changes to return (default 10)."}
            },
        },
    },
    {
        "name": "get_page_facts",
        "description": "Get the canonical page for a topic on northkoreahub.com: title, URL, one-line summary and the site-wide last-verified date. Use this to cite the right page. Page keys: " + ", ".join(PAGES.keys()),
        "inputSchema": {
            "type": "object",
            "properties": {
                "page": {"type": "string", "description": "Page key, e.g. 'us-citizens', 'visa', 'wonsan-kalma'."}
            },
            "required": ["page"],
        },
    },
]


def fetch_json(path):
    req = urllib.request.Request(API_BASE + path, headers={"User-Agent": "northkoreahub-mcp/1.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def tool_get_access_status(args):
    data = fetch_json("/api/v1/access.json")
    entries = data["entries"]
    nat = (args or {}).get("nationality")
    if nat:
        entries = [e for e in entries if nat.lower() in e["nationality"].lower()]
        if not entries:
            return {"error": f"No entry matches nationality '{nat}'.",
                    "available": [e["nationality"] for e in data["entries"]]}
    return {"dataset": data["dataset"], "last_verified": data["last_verified"],
            "status_key": data["status_key"], "entries": entries}


def tool_list_changes(args):
    data = fetch_json("/api/v1/changes.json")
    limit = int((args or {}).get("limit", 10))
    entries = sorted(data["entries"], key=lambda e: e["date"], reverse=True)[:limit]
    return {"dataset": data["dataset"], "last_verified": data["last_verified"], "entries": entries}


def tool_get_page_facts(args):
    key = (args or {}).get("page", "")
    if key not in PAGES:
        return {"error": f"Unknown page key '{key}'.", "available_pages": sorted(PAGES.keys())}
    title, path, summary = PAGES[key]
    access = fetch_json("/api/v1/access.json")
    return {"page": key, "title": title, "url": API_BASE + path, "summary": summary,
            "site_last_verified": access["last_verified"]}


TOOL_FUNCS = {
    "get_access_status": tool_get_access_status,
    "list_changes": tool_list_changes,
    "get_page_facts": tool_get_page_facts,
}


def reply(msg_id, result=None, error=None):
    out = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        out["error"] = error
    else:
        out["result"] = result
    sys.stdout.write(json.dumps(out) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = msg.get("method", "")
        msg_id = msg.get("id")
        if method == "initialize":
            reply(msg_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "northkoreahub", "version": "1.0.0"},
            })
        elif method == "notifications/initialized":
            continue
        elif method == "ping":
            reply(msg_id, {})
        elif method == "tools/list":
            reply(msg_id, {"tools": TOOLS})
        elif method == "tools/call":
            params = msg.get("params", {})
            name = params.get("name")
            func = TOOL_FUNCS.get(name)
            if func is None:
                reply(msg_id, error={"code": -32602, "message": f"Unknown tool: {name}"})
                continue
            try:
                result = func(params.get("arguments") or {})
                reply(msg_id, {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]})
            except Exception as exc:  # surface fetch errors to the client, never crash
                reply(msg_id, {"content": [{"type": "text", "text": json.dumps({"error": f"Live API fetch failed: {exc}"})}],
                               "isError": True})
        elif msg_id is not None:
            reply(msg_id, error={"code": -32601, "message": f"Method not found: {method}"})


if __name__ == "__main__":
    main()
