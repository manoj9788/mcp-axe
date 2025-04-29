import pytest
from mcp_axe.server import scan_url, scan_html_tool, scan_batch_tool, summarise_tool, ScanResult

# Mocked simple data for testing
sample_html = "<html><body><h1>Hello World</h1></body></html>"
sample_violation = {
    "id": "color-contrast",
    "impact": "critical",
    "description": "Elements must have sufficient color contrast",
    "helpUrl": "https://example.com/help"
}
sample_scan_result = {
    "url": "https://example.com",
    "violations": [sample_violation],
    "screenshot": "base64data"
}


@pytest.mark.asyncio
async def test_scan_html_tool_basic():
    """Test scanning basic HTML."""
    result = await scan_html_tool(html=sample_html)
    assert isinstance(result, ScanResult)
    assert result.url == "about:blank"  # assuming your scan_html sets it
    assert isinstance(result.violations, list)
    assert isinstance(result.screenshot, str)


@pytest.mark.asyncio
async def test_scan_batch_tool_mock():
    """Test batch scanning logic with mock URLs."""
    urls = ["https://example.com", "https://example.org"]
    # Normally would mock batch_scan, but for now assume no crash
    results = await scan_batch_tool(urls)
    assert isinstance(results, list)
    for res in results:
        assert isinstance(res, ScanResult)


@pytest.mark.asyncio
async def test_summarise_tool_single_result():
    """Test summarizing a single scan result."""
    summary = await summarise_tool(result=sample_scan_result)
    assert hasattr(summary, "total_violations")
    assert hasattr(summary, "critical")
    assert summary.total_violations >= 1


@pytest.mark.asyncio
async def test_summarise_tool_multiple_results():
    """Test summarizing multiple scan results."""
    multiple_results = [sample_scan_result, sample_scan_result]
    summary = await summarise_tool(result=multiple_results)
    assert hasattr(summary, "total_violations")
    assert summary.total_violations >= 2