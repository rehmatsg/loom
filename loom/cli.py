"""
Main entry point for the Loom CLI application.
"""
import typer

app = typer.Typer()


@app.command()
def hello():
  print(f"Loom CLI")


if __name__ == "__main__":
  app()
