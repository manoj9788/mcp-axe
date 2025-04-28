from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from mcp_axe.core import (
    scan_url_selenium,
    scan_url_playwright,
    scan_html,
    batch_scan,
    summarise_violations,
)

# Initialize
server = FastMCP("axe", version="0.1.5")

class ScanResult(BaseModel):
    url: str = Field(description="Scanned URL")
    violations: list = Field(description="Violations")
    screenshot: str = Field(description="Base64 screenshot")

@server.tool(name="scan-url", description="Accessibility scan on a URL")
async def scan_url(
    url: str = Field(description="URL to audit"),
    engine: str = Field(default="selenium", description="Engine"),
    browser: str = Field(default="chrome", description="Browser"),
    headless: bool = Field(default=True, description="Headless"),
) -> ScanResult:
    if engine == "selenium":
        data = await scan_url_selenium(url, browser, headless)
    else:
        data = await scan_url_playwright(url, browser, headless)
    return ScanResult(**data)

@server.tool(name="scan-html", description="Accessibility scan on HTML string")
async def scan_html_tool(
    html: str = Field(description="Raw HTML"),
    engine: str = Field(default="selenium", description="Engine"),
    browser: str = Field(default="chrome", description="Browser"),
    headless: bool = Field(default=True, description="Headless"),
) -> ScanResult:
    data = await scan_html(html, engine, browser, headless)
    return ScanResult(**data)

@server.tool(name="scan-batch", description="Batch scan multiple URLs")
async def scan_batch_tool(
    urls: list[str] = Field(description="List of URLs"),
    engine: str = Field(default="selenium", description="Engine"),
    browser: str = Field(default="chrome", description="Browser"),
    headless: bool = Field(default=True, description="Headless"),
) -> list[ScanResult]:
    raw = await batch_scan(urls, engine, browser, headless)
    return [ScanResult(**r) for r in raw]

@server.tool(name="summarise-violations", description="Summarise violations")
async def summarise_tool(
    result: dict = Field(description="Raw scan result"),
) -> list:
    return await summarise_violations(result)

# if you still want HTTP endpoints you can expose them here...
# app = server.fastapi_app

# ——— stdio entry point ———
def main():
    import asyncio
    # note: run_stdio_async(), not run_stdio()
    asyncio.run(server.run_stdio_async())

if __name__ == "__main__":
    main()