from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from mcp_axe.core import scan_url_selenium, scan_url_playwright, scan_html, batch_scan, summarise_violations

# Initialize the FastMCP server with plugin name and version
server = FastMCP("axe", version="0.1.4")

class ScanResult(BaseModel):
    url: str = Field(description="Scanned URL")
    violations: list = Field(description="List of violations from Axe-core")
    screenshot: str = Field(description="Base64-encoded screenshot")

@server.tool(name="scan-url", description="Perform accessibility scan on a URL")
async def scan_url(
    url: str = Field(description="URL to audit"),
    engine: str = Field(default="selenium", description="Engine to use"),
    browser: str = Field(default="chrome", description="Browser to use"),
    headless: bool = Field(default=True, description="Run browser in headless mode"),
) -> ScanResult:
    """
        Execute an accessibility scan on the specified URL.

        Args:
            url: The target URL for the scan.
            engine: The scanning engine, either 'selenium' or 'playwright'.
            browser: The browser to launch for the scan ('chrome' or 'firefox').
            headless: Whether to run the browser without a visible UI.

        Returns:
            A ScanResult containing violations and screenshot.
        """
    if engine == "selenium":
        result = await scan_url_selenium(url, browser, headless)
    else:
        result = await scan_url_playwright(url, browser, headless)
    return ScanResult(**result)

@server.tool(name="scan-html", description="Perform accessibility scan on raw HTML content")
async def scan_html_tool(
    html: str = Field(description="Raw HTML content to scan"),
    engine: str = Field(default="selenium", description="Engine to use"),
    browser: str = Field(default="chrome", description="Browser to use"),
    headless: bool = Field(default=True, description="Run browser in headless mode"),
) -> ScanResult:
    """
        Conduct an accessibility audit on the provided HTML string.

        Args:
            html: HTML source to be scanned.
            engine: Choice of scanning engine ('selenium' or 'playwright').
            browser: Browser to use for rendering ('chrome' or 'firefox').
            headless: Flag to control UI visibility during scan.

        Returns:
            A ScanResult with violation details and screenshot.
        """
    result = await scan_html(html, engine, browser, headless)
    return ScanResult(**result)

@server.tool(name="scan-batch", description="Perform batch scan of multiple URLs")
async def scan_batch(
    urls: list[str] = Field(description="List of URLs to scan"),
    engine: str = Field(default="selenium", description="Engine to use"),
    browser: str = Field(default="chrome", description="Browser to use"),
    headless: bool = Field(default=True, description="Run browser in headless mode"),
) -> list[ScanResult]:
    """
        Run accessibility scans against a list of URLs in batch.

        Args:
            urls: Collection of URLs to audit.
            engine: Scanning engine selection.
            browser: Browser for rendering pages.
            headless: Headless mode toggle.

        Returns:
            A list of ScanResult models, one per URL.
        """
    results = await batch_scan(urls, engine, browser, headless)
    return [ScanResult(**r) for r in results]

@server.tool(name="summarise-violations", description="Summarise accessibility violations")
async def summarise_violations_tool(
    result: dict = Field(description="Raw Axe-core scan result"),
) -> list:
    """
        Summarize the list of violations from a prior scan result.

        Args:
            result: The detailed scan output dict provided by scan-url or scan-html.

        Returns:
            A simplified list of violation summaries.
        """
    return await summarise_violations(result)

#Expose an SSE-based ASGI app for MCP clients
app = server.sse_app()