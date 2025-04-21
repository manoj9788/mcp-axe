import asyncio
import base64
import time
import requests
import tempfile
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from axe_selenium_python import Axe
from playwright.async_api import async_playwright

AXE_STATIC = Path(__file__).parent / "static" / "axe.min.js"
TTL_SECONDS = 24 * 3600  # refresh daily

def ensure_axe_js():
    if AXE_STATIC.exists() and time.time() - AXE_STATIC.stat().st_mtime < TTL_SECONDS:
        return AXE_STATIC.read_text()
    api_url = "https://api.github.com/repos/dequelabs/axe-core/releases/latest"
    resp = requests.get(api_url, timeout=10)
    resp.raise_for_status()
    tag = resp.json().get("tag_name")
    raw_url = f"https://cdn.jsdelivr.net/npm/axe-core@{tag}/axe.min.js"
    js_resp = requests.get(raw_url, timeout=10)
    js_resp.raise_for_status()
    AXE_STATIC.parent.mkdir(parents=True, exist_ok=True)
    AXE_STATIC.write_text(js_resp.text)
    return js_resp.text

async def scan_url_selenium(url: str, browser: str, headless: bool):
    opts = ChromeOptions() if browser == "chrome" else FirefoxOptions()
    if headless:
        opts.add_argument("--headless")
    driver = webdriver.Chrome(options=opts) if browser == "chrome" else webdriver.Firefox(options=opts)
    try:
        driver.get(url)
        axe = Axe(driver)
        axe.inject()
        results = axe.run()
        screenshot = driver.get_screenshot_as_base64()
        return {
            "url": url,
            "violations": results["violations"],
            "screenshot": screenshot,
        }
    finally:
        driver.quit()

async def scan_url_playwright(url: str, browser: str, headless: bool):
    """
    Launch Playwright, inject Axe-core from our cache (or freshly fetched), run the scan,
    take a full-page screenshot, and return violations + screenshot.
    """
    async with async_playwright() as p:
        # pick engine
        bs = p.chromium if browser == "chrome" else p.firefox

        browser_ctx = await bs.launch(headless=headless)

        page = await browser_ctx.new_page()
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")

        # inject axe-core
        axe_source = ensure_axe_js()
        await page.add_script_tag(content=axe_source)
        # Validate that axe actually got injected
        #Now note that ensure_axe_js() is a synchronous function that returns a string, not a coroutine.
        #But you're in an async context with Playwright, so Playwright may not have finished loading the page or the DOM
        # before script injection.
        injected = await page.evaluate("typeof axe !== 'undefined'")
        if not injected:
            raise RuntimeError("Axe failed to inject into the page.")

        # run the audit
        result = await page.evaluate("async () => await axe.run()")

        # capture screenshot
        buffer = await page.screenshot(full_page=True)
        screenshot = base64.b64encode(buffer).decode()

        await browser_ctx.close()

        return {
            "url": url,
            "violations": result["violations"],
            "screenshot": screenshot,
        }

async def scan_html(html_content: str, browser: str = "chrome", headless: bool = True):
    """
    Save provided HTML to a temp file and run Axe-core scan using Playwright.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as tmp:
        tmp.write(html_content)
        tmp_path = tmp.name

    async with async_playwright() as p:
        bs = p.chromium if browser == "chrome" else p.firefox
        browser_ctx = await bs.launch(headless=headless)
        page = await browser_ctx.new_page()
        await page.goto(f"file://{tmp_path}")

        axe_source = ensure_axe_js()
        await page.add_script_tag(content=axe_source)

        result = await page.evaluate("async () => await axe.run()")

        buffer = await page.screenshot(full_page=True)
        screenshot = base64.b64encode(buffer).decode()

        await browser_ctx.close()

        return {
            "html_file": tmp_path,
            "violations": result["violations"],
            "screenshot": screenshot,
        }

async def batch_scan(urls: list, engine: str = "playwright", browser: str = "chrome", headless: bool = True):
    """
    Run Axe-core scan on multiple URLs. Supports Playwright or Selenium engine.
    """
    results = {}

    for url in urls:
        try:
            if engine == "selenium":
                results[url] = await scan_url_selenium(url, browser, headless)
            else:
                results[url] = await scan_url_playwright(url, browser, headless)
        except Exception as e:
            results[url] = {"error": str(e)}

    return results

async def summarise_violations(result: dict):
    """
    Generate summary from Axe-core results.
    """
    if not result or "violations" not in result:
        return "No violations found or invalid result format."

    summary = []
    for v in result["violations"]:
        summary.append({
            "id": v["id"],
            "impact": v.get("impact", "unknown"),
            "description": v["description"],
            "nodes_affected": len(v["nodes"]),
        })
    return summary