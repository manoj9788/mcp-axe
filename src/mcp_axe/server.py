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
server = FastMCP("axe", version="0.1.6")

class ScanResult(BaseModel):
    url: str = Field(description="Scanned URL")
    violations: list = Field(description="List of accessibility violations")


@server.tool(name="scan-url", description="Accessibility scan on a URL")
async def scan_url(
    url: str = Field(description="URL to audit")
    ) -> ScanResult:
    data = await scan_url_selenium(url, browser="chrome", headless=True)
    return ScanResult(url=data["url"], violations=data["violations"])


@server.tool(name="scan-html", description="Accessibility scan on raw HTML string")
async def scan_html_tool(html: str = Field(description="Raw HTML to audit")
    ) -> ScanResult:
    data = await scan_html(html, browser="chrome", headless=True)
    # data["html_file"] contains the temp‐file path
    return ScanResult(url=data["html_file"], violations=data["violations"])


@server.tool(name="scan-batch", description="Batch scan multiple URLs")
async def scan_batch_tool(
    urls: list[str] = Field(..., description="List of URLs to audit"),
) -> list[ScanResult]:
    # do a Selenium+Chrome+headless run on each URL
    raw = await batch_scan(urls, engine="selenium", browser="chrome", headless=True)
    return [
        ScanResult(
            url=url,
            violations=raw[url].get("violations", [])
        )
        for url in urls
    ]

@server.tool(name="summarise-violations", description="Summarise accessibility violations")
async def summarise_tool(result: dict = Field(description="Raw scan result dict")
    ) -> list:
    return await summarise_violations(result)


# — stdio entrypoint —
def main():
    import asyncio
    asyncio.run(server.run_stdio_async())

if __name__ == "__main__":
    main()