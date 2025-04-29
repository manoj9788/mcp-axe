import asyncio
import base64
import time
import requests
import tempfile
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from playwright.async_api import async_playwright

AXE_STATIC = Path(__file__).parent / "static" / "axe.min.js"
TTL_SECONDS = 24 * 3600  # refresh daily

def ensure_axe_js(force=False):
    if not force and AXE_STATIC.exists() and time.time() - AXE_STATIC.stat().st_mtime < TTL_SECONDS:
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

def inject_and_run_axe(driver, axe_source):
    driver.execute_script(axe_source)
    return driver.execute_async_script("""
        var callback = arguments[arguments.length - 1];
        try {
            axe.run().then(results => callback(results)).catch(err => callback({ error: err.message }));
        } catch (e) {
            callback({ error: e.message });
        }
    """)

async def scan_url_selenium(url: str, browser: str, headless: bool):
    opts = ChromeOptions() if browser == "chrome" else FirefoxOptions()
    if headless:
        opts.add_argument("--headless")
    driver = webdriver.Chrome(options=opts) if browser == "chrome" else webdriver.Firefox(options=opts)
    try:
        driver.get(url)
        axe_source = ensure_axe_js()
        results = inject_and_run_axe(driver, axe_source)
        if "error" in results:
            raise RuntimeError(f"Axe injection or run failed: {results['error']}")
        return {
            "url": url,
            "violations": results.get("violations", []),
        }
    finally:
        driver.quit()

async def scan_url_playwright(url: str, browser: str, headless: bool):
    async with async_playwright() as p:
        bs = p.chromium if browser == "chrome" else p.firefox
        ctx = await bs.launch(headless=headless)
        page = await ctx.new_page()
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")
        axe_source = ensure_axe_js()
        await page.add_script_tag(content=axe_source)
        injected = await page.evaluate("typeof axe !== 'undefined'")
        if not injected:
            raise RuntimeError("Axe failed to inject into the page.")
        result = await page.evaluate("async () => await axe.run()")
        buff = await page.screenshot(full_page=True)
        await ctx.close()
        return {
            "url": url,
            "violations": result.get("violations", []),
        }

async def scan_html(html_content: str, browser: str = "chrome", headless: bool = True):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as tmp:
        tmp.write(html_content)
        tmp_path = tmp.name
    async with async_playwright() as p:
        bs = p.chromium if browser == "chrome" else p.firefox
        ctx = await bs.launch(headless=headless)
        page = await ctx.new_page()
        await page.goto(f"file://{tmp_path}")
        axe_source = ensure_axe_js()
        await page.add_script_tag(content=axe_source)
        result = await page.evaluate("async () => await axe.run()")
        buff = await page.screenshot(full_page=True)
        await ctx.close()
        return {
            "html_file": tmp_path,
            "violations": result.get("violations", []),
        }

async def batch_scan(urls: list, engine: str = "selenium", browser: str = "chrome", headless: bool = True):
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
    if "violations" not in result:
        return []
    summary = []
    for v in result["violations"]:
        summary.append({
            "id": v["id"],
            "impact": v.get("impact", "unknown"),
            "description": v["description"],
            "nodes_affected": len(v.get("nodes", [])),
        })
    return summary
