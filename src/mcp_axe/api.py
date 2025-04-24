from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Literal, Optional
import asyncio

from mcp_axe.core import scan_url_selenium, scan_url_playwright, scan_html, batch_scan, summarise_violations

app = FastAPI(title="mcp-axe API")


class ScanRequest(BaseModel):
    url: str
    browser: Literal["chrome", "firefox"] = "chrome"
    headless: bool = True
    engine: Literal["selenium", "playwright"] = "selenium"

@app.post("/scan/url")
async def scan_url(req: ScanRequest):
    if req.engine == "playwright":
        return await scan_url_playwright(req.url, req.browser, req.headless)
    return await scan_url_selenium(req.url, req.browser, req.headless)


class HTMLScanRequest(BaseModel):
    html: str
    browser: Literal["chrome", "firefox"] = "chrome"
    headless: bool = True

@app.post("/scan/html")
async def scan_html(req: HTMLScanRequest):
    return await scan_html(req.html, req.browser, req.headless)


class BatchScanRequest(BaseModel):
    urls: List[str]
    browser: Literal["chrome", "firefox"] = "chrome"
    headless: bool = True
    engine: Literal["selenium", "playwright"] = "playwright"

@app.post("/scan/batch")
async def scan_batch(req: BatchScanRequest):
    return await batch_scan(req.urls, req.engine, req.browser, req.headless)


class SummariseRequest(BaseModel):
    result: dict

@app.post("/scan/summarise")
async def summarise_violations_api(req: SummariseRequest):
    return await summarise_violations(req.result)


# CLI entry point for terminal use
if __name__ == "__main__":
    app.cli()