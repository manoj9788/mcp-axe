from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from mcp_axe.core import scan_url_selenium,scan_html

app = FastAPI(title="mcp-axe API")

class ScanRequest(BaseModel):
    url: str
    browser: str
    headless: bool = True
    save: bool = False
    format: str = "json"


class HTMLScanRequest(BaseModel):
    html: str
    browser: str = "chrome"
    headless: bool = True

@app.post("/scan/url")
async def scan_url(req: ScanRequest):
    if req.browser not in ("chrome", "firefox"):
        raise HTTPException(status_code=400, detail="Unsupported browser")
    result = await scan_url_selenium(req.url, req.browser, req.headless)
    return result

@app.post("/scan/html")
async def scan_html_string(req: HTMLScanRequest):
    if req.browser not in ("chrome", "firefox"):
        raise HTTPException(status_code=400, detail="Unsupported browser")
    return await scan_html(req.html, req.browser, req.headless)