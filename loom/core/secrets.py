"""
Secrets management module for macOS keychain operations.
"""
import keyring
import typer
from typing import Optional, List
from rich.console import Console

console = Console()

class SecretsManager:
  """Manages secrets using macOS keychain via keyring."""

  def __init__(self, service_name: str = "loom"):
    self.service_name = service_name

  def save_secret(self, key: str, value: str) -> bool:
    """Save a secret to keychain."""
    try:
      keyring.set_password(self.service_name, key, value)
      return True
    except Exception as e:
      console.print(f"[red]Error saving secret '{key}': {e}[/red]")
      return False

  def get_secret(self, key: str) -> Optional[str]:
    """Retrieve a secret from keychain."""
    try:
      return keyring.get_password(self.service_name, key)
    except Exception as e:
      console.print(f"[red]Error retrieving secret '{key}': {e}[/red]")
      return None

  def delete_secret(self, key: str) -> bool:
    """Delete a secret from keychain."""
    try:
      keyring.delete_password(self.service_name, key)
      return True
    except Exception as e:
      console.print(f"[red]Error deleting secret '{key}': {e}[/red]")
      return False

  def list_secrets(self) -> List[str]:
    """List all secrets (limited functionality with keyring)."""
    # Note: keyring doesn't provide a direct way to list all keys
    # This is a limitation of the keyring library
    console.print(
        "[yellow]Note: keyring doesn't support listing all secrets directly.[/yellow]")
    console.print(
        "[yellow]You'll need to know the key names to retrieve them.[/yellow]")
    return []



# CLI Commands
def save_secret(key: str, value: str, service: str = "loom"):
  """Save a secret to keychain."""
  manager = SecretsManager(service)
  if manager.save_secret(key, value):
    console.print(f"[green]✓ Secret '{key}' saved successfully[/green]")
  else:
    raise typer.Exit(1)


def get_secret(key: str, service: str = "loom", show_key: bool = False):
  """Retrieve a secret from keychain."""
  manager = SecretsManager(service)
  value = manager.get_secret(key)

  if value is None:
    console.print(f"[red]✗ Secret '{key}' not found[/red]")
    raise typer.Exit(1)

  if show_key:
    console.print(f"[green]{key}: {value}[/green]")
  else:
    console.print(f"[green]{value}[/green]")


def delete_secret(key: str, service: str = "loom"):
  """Delete a secret from keychain."""
  manager = SecretsManager(service)
  if manager.delete_secret(key):
    console.print(f"[green]✓ Secret '{key}' deleted successfully[/green]")
  else:
    console.print(f"[red]✗ Failed to delete secret '{key}'[/red]")
    raise typer.Exit(1)


def list_secrets(service: str = "loom"):
  """List all secrets (with limitations)."""
  manager = SecretsManager(service)
  manager.list_secrets()

