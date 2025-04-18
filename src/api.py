from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from mcp_axe.core import scan_url_selenium

app = FastAPI(title="mcp-axe API")

class ScanRequest(BaseModel):
    url: str
    browser: str
    headless: bool = True
    save: bool = False
    format: str = "json"

@app.post("/scan/url")
async def scan_url(req: ScanRequest):
    if req.browser not in ("chrome", "firefox"):
        raise HTTPException(status_code=400, detail="Unsupported browser")
    result = await scan_url_selenium(req.url, req.browser, req.headless)
    return result
