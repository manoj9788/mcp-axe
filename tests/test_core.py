import pytest
from mcp_axe.core import (
    scan_url_selenium,
    scan_url_playwright,
    scan_html,
    batch_scan,
    summarise_violations
)

@pytest.mark.asyncio
async def test_scan_url_selenium_valid_url():
    result = await scan_url_selenium("https://example.com", browser="chrome", headless=True)
    assert isinstance(result, dict)
    assert "url" in result
    assert "violations" in result
    assert "screenshot" in result

@pytest.mark.asyncio
async def test_scan_url_playwright_valid_url():
    result = await scan_url_playwright("https://example.com", browser="chrome", headless=True)
    assert isinstance(result, dict)
    assert "url" in result
    assert "violations" in result
    assert "screenshot" in result

@pytest.mark.asyncio
async def test_scan_html_basic():
    html_content = "<html><head><title>Test</title></head><body><h1>Hello World</h1></body></html>"
    result = await scan_html(html_content, browser="chrome", headless=True)
    assert "violations" in result
    assert "screenshot" in result
    assert result["html_file"].endswith(".html")

@pytest.mark.asyncio
async def test_batch_scan_mixed():
    urls = ["https://example.com", "https://w3.org"]
    result = await batch_scan(urls, engine="playwright", browser="chrome", headless=True)
    assert isinstance(result, dict)
    for url in urls:
        assert "violations" in result[url] or "error" in result[url]

@pytest.mark.asyncio
async def test_summarise_output_format():
    mock_result = {
        "violations": [
            {
                "id": "color-contrast",
                "impact": "serious",
                "description": "Ensures the contrast between foreground and background colors is sufficient",
                "nodes": [{}] * 3
            }
        ]
    }

    summary = await summarise_violations(mock_result)
    assert isinstance(summary, list)
    assert summary[0]["id"] == "color-contrast"
    assert summary[0]["impact"] == "serious"
    assert summary[0]["nodes_affected"] == 3