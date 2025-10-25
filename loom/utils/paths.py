import os

APP_NAME = "Loom"

def get_working_dir():
  base_dir = os.path.expanduser(f"~/Library/Application Support/{APP_NAME}")
  os.makedirs(base_dir, exist_ok=True)
  return base_dir

def get_database_dir():
  return os.path.join(get_working_dir(), "db")