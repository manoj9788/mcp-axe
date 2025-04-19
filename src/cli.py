import typer
import json
import asyncio
from typing import List
from mcp_axe.core import scan_url_selenium, scan_url_playwright, scan_html, summarise, batch_scan

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
        violations_summary = summarise(result)
        typer.secho(f"Found {len(violations_summary)} accessibility issues:", fg=typer.colors.BLUE, bold=True)
        for item in violations_summary:
            typer.secho(f"- {item['id']} ({item['impact']}): {item['nodes_affected']} instances",
                        fg=typer.colors.RED if item['impact'] == 'critical' else typer.colors.YELLOW)


if __name__ == "__main__":
    app()