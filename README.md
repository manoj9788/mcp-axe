# mcp-axe

[![PyPI version](https://img.shields.io/pypi/v/mcp-axe.svg)](https://pypi.org/project/mcp-axe/)

# 🧪 mcp-axe: Accessibility Testing Plugin using Axe-core

`mcp-axe` is an MCP-compatible plugin for automated accessibility scanning using Deque's [axe-core](https://github.com/dequelabs/axe-core). It supports 
both **Selenium** and **Playwright** engines and provides a CLI and FastAPI interface for scanning URLs, 
raw HTML content, and batches.


## 📦 Installation

### PyPI
You could use mcp-axe from pypi package
`https://pypi.org/project/mcp-axe/`

## CLI Usage

### Scan a URL
```bash
mcp-axe scan-url https://broken-workshop.dequelabs.com --engine selenium --no-headless --save --output-json --output-html
```

### Scan a local HTML file
```bash
mcp-axe scan-html path/to/your/file.html --browser chrome --no-headless --save --output-json --output-html
```

### Batch scan multiple URLs:
```bash
mcp-axe batch-scan "https://broken-workshop.dequelabs.com,https://google.com" --engine selenium --browser chrome --headless --save --output-json
```

### Summarize a saved report:
```bash
mcp-axe summarize report_selenium_chrome.json --output-json --save
```

## API Usage
Clone this repo and install in editable mode:

```bash
#optional
#git clone https://github.com/yourname/mcp-axe.git
#cd mcp-axe

python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

### Run the FastAPI server For local development:
```bash
make run
#uvicorn mcp_axe.api:app --reload --app-dir src
```

### Available Endpoints:

| Endpoint           | Description             |
|--------------------|--------------------------|
| `POST /scan/url`   | Scan a live URL          |
| `POST /scan/html`  | Scan raw HTML content    |
| `POST /scan/batch` | Scan multiple URLs       |
| `POST /scan/summarise` | Summarize violations |

### Run CLI
```bash
curl -X POST http://localhost:9788/scan/url \
  -H "Content-Type: application/json" \
  -d '{
        "url": "https://broken-workshop.dequelabs.com",
        "engine": "selenium",
        "browser": "chrome",
        "headless": true
      }'
```

```bash
curl -X POST http://localhost:9788/scan/html \
  -H "Content-Type: application/json" \
  -d '{
        "html": "<!DOCTYPE html><html><body><h1>Test</h1><p>Hello World</p></body></html>",
        "browser": "chrome",
        "headless": true
      }'
```


```bash 
curl -X POST http://localhost:9788/scan/batch \
  -H "Content-Type: application/json" \
  -d '{
        "urls": [
          "https://broken-workshop.dequelabs.com",
          "https://google.com"
        ],
        "engine": "selenium",
        "browser": "firefox",
        "headless": true
      }'
```
```bash
Run Test:
make test
```
### MCP Client

## Cursor
```bash
{
  "mcpServers": {
    "mcp-axe": {
      "command": "mcp-axe",
      "args": ["run", "--port", "9788"]
    }
  }
}```

## Claude
```bash
{
  "mcpServers": {
    "mcp-axe": {
      "command": "mcp-axe",
      "args": ["run", "--port", "9788"],
      "workingDirectory": "${projectRoot}",
      "port": 9788,
      "transport": "sse",
      "ssePath": "/sse",
      "messagePath": "/messages"
    }
  }
}```
