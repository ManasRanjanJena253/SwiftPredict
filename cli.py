import click
import subprocess
import webbrowser

@click.group()
def cli():
    pass

@cli.command()
def ui():
    """Launch SwiftPredict UI and backend"""
    subprocess.Popen(["uvicorn", "backend.app.main:app", "--reload"])
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    cli()
