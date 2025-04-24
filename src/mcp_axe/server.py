from mcp.server.fastmcp import FastMCP
import mcp.types as types

from mcp_axe.core import scan_url_selenium, scan_url_playwright, scan_html,summarise_violations, batch_scan

server = FastMCP("axe", version="0.3.0")

@server.tool(name="scan-url")
async def scan_url(
    url: types.String(description="URL to audit"),
    engine: types.String = types.Option(default="selenium", enum=["selenium","playwright"]),
    browser: types.String = types.Option(default="chrome", enum=["chrome", "firefox"]),
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

@server.tool(name="scan-html-string")
async def scan_html(
    html: types.String(description="HTML content to audit"),
    browser: types.String = types.Option(default="chrome"),
    headless: types.Boolean = types.Option(default=True),
) -> types.Object(
    description="Accessibility scan result from raw HTML input",
    properties={
        "html_file": types.String(),
        "violations": types.Array(items=types.Any()),
        "screenshot": types.String(),
    }
):
    return await scan_html(html, browser, headless)

@server.tool(name="batch-url-scan")
async def batch_scan(
    urls: types.Array(description="List of URLs to audit", items=types.String()),
    engine: types.String = types.Option(default="playwright", enum=["selenium", "playwright"]),
    browser: types.String = types.Option(default="chrome"),
    headless: types.Boolean = types.Option(default=True),
) -> types.Object(description="Batch scan results per URL", additionalProperties=True):
    return await batch_scan(urls, engine, browser, headless)


@server.tool(name="summarise-violations")
async def summarise(
    result: types.Object(description="Raw Axe-core result with violations", additionalProperties=True)
) -> types.Array(
    description="Summarised view of violations",
    items=types.Object(
        properties={
            "id": types.String(),
            "impact": types.String(),
            "description": types.String(),
            "nodes_affected": types.Integer(),
        }
    )
):
    return await summarise_violations(result)

app = server.fastapi_app