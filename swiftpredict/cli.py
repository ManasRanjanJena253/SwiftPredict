import click
import subprocess
import webbrowser
import sys
import importlib.resources
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parent.parent.resolve()


@click.group()
def cli():
    """SwiftPredict Command Line Interface"""
    pass


@cli.command("launch")
@click.argument("target")
def launch(target):
    """
    Launch SwiftPredict components.

    Example:
        swiftpredict launch ui
    """
    if target != "ui":
        click.echo("Invalid target. Try: swiftpredict launch ui")
        return

    backend_dir = PACKAGE_ROOT / "backend" / "app"

    if not backend_dir.exists():
        click.echo(f"Backend directory not found at {backend_dir}.")
        click.echo("Make sure the package was installed correctly.")
        return

    click.echo("Starting SwiftPredict backend (FastAPI)...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.logger_apis:app", "--reload"],
        cwd=str(backend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    click.echo("Backend running at http://localhost:8000")

    # Resolve index.html from inside the installed package
    try:
        with importlib.resources.path("swiftpredict", "index.html") as ui_path:
            click.echo(f"Opening UI...")
            webbrowser.open(Path(ui_path).as_uri())
    except FileNotFoundError:
        click.echo("UI file not found inside the package. Try reinstalling swiftpredict.")

    click.echo("Press Ctrl+C to stop the backend...")

    try:
        backend_process.wait()
    except KeyboardInterrupt:
        click.echo("\nStopping SwiftPredict backend...")
        backend_process.terminate()
        backend_process.wait()
        click.echo("Backend stopped cleanly.")