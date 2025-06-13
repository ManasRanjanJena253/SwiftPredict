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
    if target == "ui":
        click.echo("Launching SwiftPredict backend (FastAPI)...")
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.app.api.logger_apis:app", "--reload"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        click.echo("Launching SwiftPredict frontend (Next.js)...")
        try:
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=os.path.join(os.getcwd(), "frontend"),  # adjust if your frontend is in a different folder
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except FileNotFoundError:
            click.echo("❌ Could not find npm or frontend directory.")
            return

        # Wait a few seconds before launching in browser
        time.sleep(5)
        webbrowser.open("http://localhost:3000")  # assuming default Next.js dev server port

        click.echo("SwiftPredict UI launched at http://localhost:3000")
        click.echo("FastAPI backend running at http://localhost:8000")

        # Optional: Keep CLI process running until killed
        try:
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            click.echo("Stopping processes...")
            backend_process.terminate()
            frontend_process.terminate()
    else:
        click.echo("Invalid target. Try: swiftpredict launch ui")


if __name__ == "__main__":
    cli()