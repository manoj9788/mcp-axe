import typer
import json
import asyncio
import uvicorn
from typing import List
from mcp_axe.core import scan_url_selenium, scan_url_playwright, scan_html, summarise_violations, batch_scan

app = typer.Typer(
    no_args_is_help=True,
    help="Run Axe-core accessibility scans"
)

@app.command("scan-url")
def scan_url_cmd(
        url: str = typer.Argument(..., help="URL to scan"),
        browser: str = typer.Option("chrome", "--browser", help="chrome or firefox"),
        headless: bool = typer.Option(True, "--headless/--no-headless", help="Run browser headless"),
        engine: str = typer.Option("selenium", "--engine",
                                   help="Scanning engine: 'selenium' (default) or 'playwright'"),
        output_json: bool = typer.Option(False, "--output-json", help="Print JSON report"),
        output_html: bool = typer.Option(False, "--output-html", help="Generate HTML report file"),
        save: bool = typer.Option(False, "--save", help="Save report files to disk")
):
    """Scan a URL for accessibility issues."""
    # Choose engine function
    if engine == "selenium":
        scan_fn = scan_url_selenium
    elif engine == "playwright":
        scan_fn = scan_url_playwright
    else:
        typer.secho(f"❌ Unknown engine '{engine}'.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Perform scan
    result = asyncio.run(scan_fn(url, browser, headless))

    _handle_output(result, url, engine, browser, output_json, output_html, save)


@app.command("scan-html")
def scan_html_cmd(
        html_file: str = typer.Argument(..., help="HTML file to scan"),
        browser: str = typer.Option("chrome", "--browser", help="chrome or firefox"),
        headless: bool = typer.Option(True, "--headless/--no-headless", help="Run browser headless"),
        output_json: bool = typer.Option(False, "--output-json", help="Print JSON report"),
        output_html: bool = typer.Option(False, "--output-html", help="Generate HTML report file"),
        save: bool = typer.Option(False, "--save", help="Save report files to disk")
):
    """Scan HTML content for accessibility issues."""
    try:
        with open(html_file, 'r') as f:
            html_content = f.read()
    except Exception as e:
        typer.secho(f"❌ Error reading HTML file: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    result = asyncio.run(scan_html(html_content, browser, headless))

    _handle_output(result, html_file, "html-scan", browser, output_json, output_html, save)


@app.command("batch-scan")
def batch_scan_cmd(
        urls: List[str] = typer.Argument(..., help="URLs to scan (comma-separated)"),
        browser: str = typer.Option("chrome", "--browser", help="chrome or firefox"),
        headless: bool = typer.Option(True, "--headless/--no-headless", help="Run browser headless"),
        engine: str = typer.Option("playwright", "--engine",
                                   help="Scanning engine: 'playwright' (default) or 'selenium'"),
        output_json: bool = typer.Option(False, "--output-json", help="Print JSON report"),
        output_html: bool = typer.Option(False, "--output-html", help="Generate HTML report file"),
        save: bool = typer.Option(False, "--save", help="Save report files to disk")
):
    """Batch scan multiple URLs for accessibility issues."""
    if engine not in ["selenium", "playwright"]:
        typer.secho(f"❌ Unknown engine '{engine}'.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Handle comma-separated URLs
    if len(urls) == 1 and ',' in urls[0]:
        urls = [url.strip() for url in urls[0].split(',')]

    result = asyncio.run(batch_scan(urls, engine, browser, headless))

    _handle_output(result, "batch-scan", engine, browser, output_json, output_html, save)


@app.command("summarize")
def summarize_cmd(
        input_file: str = typer.Argument(..., help="JSON file with scan results to summarize"),
        output_json: bool = typer.Option(False, "--output-json", help="Print JSON summary"),
        save: bool = typer.Option(False, "--save", help="Save summary file to disk")
):
    """Summarize accessibility violations from a scan result."""
    try:
        with open(input_file, 'r') as f:
            result = json.load(f)
    except Exception as e:
        typer.secho(f"❌ Error reading input file: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    summary = asyncio.run(summarise_violations(result))

    if output_json or save:
        payload = json.dumps(summary, default=str, indent=2)
        typer.echo(payload)
        if save:
            path_json = f"summary_{input_file.replace('.json', '')}.json"
            with open(path_json, "w") as f:
                f.write(payload)
            typer.secho(f"🔖 Summary saved: {path_json}", fg=typer.colors.GREEN)
    else:
        # Display a nicer formatted summary
        typer.secho(f"Summary of violations:", fg=typer.colors.BLUE, bold=True)
        for item in summary:
            typer.secho(f"ID: {item['id']}", fg=typer.colors.YELLOW)
            typer.secho(f"Impact: {item['impact']}",
                        fg=typer.colors.RED if item['impact'] == 'critical' else typer.colors.YELLOW)
            typer.secho(f"Description: {item['description']}")
            typer.secho(f"Nodes affected: {item['nodes_affected']}")
            typer.echo("---")


@app.command("run")
def run_server(port: int = 8011):
    uvicorn.run("mcp_axe.api:app", app_dir="src", port=port, reload=False)

def _handle_output(result, source, engine, browser, output_json, output_html, save):
    """Helper function to handle output for scan commands."""
    if output_json or save:
        payload = json.dumps(result, default=str, indent=2)
        if output_json:
            typer.echo(payload)
        if save:
            path_json = f"report_{engine}_{browser}.json"
            with open(path_json, "w") as f:
                f.write(payload)
            typer.secho(f"🔖 JSON report saved: {path_json}", fg=typer.colors.GREEN)

    if output_html or save:
        html = f"""<html>
  <head><title>Report for {source}</title></head>
  <body>
    <h1>Accessibility Report for {source}</h1>
    <pre>{json.dumps(result, indent=2)}</pre>
  </body>
</html>"""
        if save:
            path_html = f"report_{engine}_{browser}.html"
            with open(path_html, "w") as f:
                f.write(html)
            typer.secho(f"🔖 HTML report saved: {path_html}", fg=typer.colors.GREEN)

    # Display a summary if not outputting JSON
    if not output_json:
        violations_summary = asyncio.run(summarise_violations(result))
        typer.secho(f"Found {len(violations_summary)} accessibility issues:", fg=typer.colors.BLUE, bold=True)
        for item in violations_summary:
            typer.secho(f"- {item['id']} ({item['impact']}): {item['nodes_affected']} instances",
                        fg=typer.colors.RED if item['impact'] == 'critical' else typer.colors.YELLOW)


if __name__ == "__main__":
    app()