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



## API Usage
Clone this repo and install in editable mode:

```bash
#optional
#git clone https://github.com/yourname/mcp-axe.git
#cd mcp-axe

python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

### MCP Client

If you install direct from pip The configure Claude as below

```bash
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
If you are on development mode then configure claude as below
```bash
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