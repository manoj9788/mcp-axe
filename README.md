# mcp‑axe 

[![PyPI version](https://img.shields.io/pypi/v/mcp-axe.svg)](https://pypi.org/project/mcp-axe/) [![License](https://img.shields.io/pypi/l/mcp-axe.svg)](LICENSE)

---

A **Model Context Protocol** (MCP) plugin for automated accessibility testing using [axe-core](https://github.com/dequelabs/axe-core). It lets MCP‑aware clients (Claude Desktop, Cursor, etc.) or your terminal run:

- **Single URL scans**
- **HTML string scans**
- **Batch URL scans**
- **Violation summarisation**

All powered by Selenium under the hood.

## 📦 Installation

### From PyPI

```bash
pip install mcp-axe
```
_Requires Python 3.8+._



### Local / Development

```bash
git clone https://github.com/manoj9788/mcp-axe.git
cd mcp-axe
python3 -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

---

## 🔧 Usage

### MCP (JSON‑RPC) mode

For AI clients (e.g. Claude Desktop, Cursor, VS Code MCP extension), configure your `<client>_config.json`:

```json
{
  "mcpServers": {
    "axe-a11y": {
      "command": "python3",
      "args": ["-m", "mcp_axe"],
      "cwd": "."
    }
  }
}
```

Once the MCP server is running, you can invoke tools like:
- `scan-url` (params: `{ "url": "https://google.com" }`)
- `scan-html` (params: `{ "html": "<h1>Hello</h1>" }`)
- `scan-batch` (params: `{ "urls": ["https://a.com","https://b.com"] }`)
- `summarise-violations` (params: `{ "result": <axe result> }`)

### MCP local dev mode
```json
{
  "mcpServers": {
    "axe-a11y": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "mcp_axe"],
      "cwd": "/path/to/mcp-axe"
    }
  }
}
```


### FastAPI REST mode (optional)

Expose HTTP endpoints via:

```python
from mcp_axe.server import app  # FastAPI instance
import uvicorn

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=9788, reload=True)
```

Then:
```bash
curl -X POST http://localhost:9788/scan/url -H 'Content-Type: application/json' \
  -d '{ "url": "https://google.com" }'
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch (`git checkout -b feature/xyz`)
3. Commit your changes
4. Open a PR

---

## 📜 License

[MIT](LICENSE)

