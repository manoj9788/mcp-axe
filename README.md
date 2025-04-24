# 🧪 mcp-axe: Accessibility Testing Plugin using Axe-core

`mcp-axe` is an MCP-compatible plugin for automated accessibility scanning using Deque's [axe-core](https://github.com/dequelabs/axe-core). It supports both **Selenium** and **Playwright** engines and provides a CLI and FastAPI interface for scanning URLs, raw HTML content, and batches — all enriched with screenshot capture and optional reporting.


## 📦 Installation

Clone this repo and install in editable mode:

```bash
#git clone https://github.com/yourname/mcp-axe.git
#cd mcp-axe
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
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

## API Usage

### Run the FastAPI server locally:
```bash
uvicorn mcp_axe.api:app --reload --app-dir src
```

### Available Endpoints:

| Endpoint           | Description             |
|--------------------|--------------------------|
| `POST /scan/url`   | Scan a live URL          |
| `POST /scan/html`  | Scan raw HTML content    |
| `POST /scan/batch` | Scan multiple URLs       |
| `POST /scan/summarise` | Summarize violations |
