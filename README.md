# mcp-axe



## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install .
```


## CLI Usage

### For scanning a URL
```bash
mcp-axe scan-url https://broken-workshop.dequelabs.com --engine selenium --no-headless --save --output-json --output-html
```