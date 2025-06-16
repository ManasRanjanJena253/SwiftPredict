import click
import subprocess
import webbrowser
import time
import os
import sys


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

    click.echo("Launching SwiftPredict backend (FastAPI)...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload"],
        cwd=os.path.join(os.getcwd(), "backend", "app"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    click.echo("Launching SwiftPredict frontend (Next.js)...")
    try:
        frontend_process = subprocess.Popen(
            "npm run dev",
            shell=True,  # Needed on Windows to resolve npm
            cwd=os.path.join(os.getcwd(), "frontend"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        click.echo(f"Failed to launch frontend: {e}")
        backend_process.terminate()
        return

    # Give frontend time to initialize, then launch in browser
    time.sleep(5)
    webbrowser.open("http://localhost:3000")

    click.echo("SwiftPredict UI launched at http://localhost:3000")
    click.echo("FastAPI backend running at http://localhost:8000")
    click.echo("Press Ctrl+C to stop both services...")

    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        click.echo("\nStopping SwiftPredict services...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        click.echo("All processes terminated cleanly.")
