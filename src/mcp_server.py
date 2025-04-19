import mcp.types as types
from mcp.server.fastmcp import FastMCP
from mcp_axe.core import scan_url_selenium, scan_url_playwright
mcp_server = FastMCP("axe", version="0.3.0")

@mcp_server.tool(name="scan-url")
async def scan_url(
    url: types.String(description="URL to audit"),
    engine: types.String = types.Option(default="selenium", enum=["selenium","playwright"]),
    browser: types.String = types.Option(default="chrome"),
    headless: types.Boolean = types.Option(default=True),
) -> types.Object(
    description="Accessibility scan result",
    properties={
        "url": types.String(),
        "violations": types.Array(items=types.Any()),
        "screenshot": types.String(),
    }
):
    if engine == "selenium":
        return await scan_url_selenium(url, browser, headless)
    return await scan_url_playwright(url, browser, headless)