import os
import json

from typing import Any, Optional
from unqlite import UnQLite

from loom.utils.paths import get_database_dir

DB_FILENAME = "db.unqlite"
PREFS_PREFIX = "prefs:"

class Preferences:
  def __init__(self, db_path: Optional[str] = None):
    if db_path is None:
      db_path = os.path.join(get_database_dir(), DB_FILENAME)
    self._db = UnQLite(db_path)

  def _k(self, key: str) -> str:
    return f"{PREFS_PREFIX}{key}"

  def set(self, key: str, value: Any) -> None:
    """
    Save a preference. Value is JSON-encoded so you can store bool/int/float/str/list/dict.
    """
    self._db[self._k(key)] = json.dumps(value)

  def get(self, key: str, default: Any = None, type_: Optional[type] = None) -> Any:
    """
    Load a preference. If not found, returns default.
    If type_ is given, tries to cast the value (useful for str->int/bool).
    """
    k = self._k(key)
    if k not in self._db:
      return default
    try:
      value = json.loads(self._db[k])
    except Exception:
      # in case older data wasn't JSON-encoded
      value = self._db[k]
    if type_ is not None and value is not None:
      try:
        # special-case bool casting from strings
        if type_ is bool and isinstance(value, str):
          v = value.strip().lower()
          if v in ("1", "true", "yes", "y", "on"):
            return True
          if v in ("0", "false", "no", "n", "off"):
            return False
        return type_(value)
      except Exception:
        return default
    return value

  def delete(self, key: str) -> bool:
    """
    Delete a preference. Returns True if it existed.
    """
    k = self._k(key)
    if k in self._db:
      del self._db[k]
      return True
    return False

  def exists(self, key: str) -> bool:
    return self._k(key) in self._db

  def all(self) -> dict:
    """
    Return all preferences as a dict {key: value}.
    """
    out = {}
    for k, v in self._db.items():
      if isinstance(k, bytes):
        k = k.decode("utf-8", errors="ignore")
      if isinstance(v, bytes):
        v = v.decode("utf-8", errors="ignore")
      if k.startswith(PREFS_PREFIX):
        raw_key = k[len(PREFS_PREFIX):]
        try:
          out[raw_key] = json.loads(v)
        except Exception:
          out[raw_key] = v
    return out

  def clear(self) -> int:
    """
    Remove all preferences. Returns number of keys removed.
    """
    to_delete = []
    for k, _ in self._db.items():
      if isinstance(k, bytes):
        k = k.decode("utf-8", errors="ignore")
      if k.startswith(PREFS_PREFIX):
        to_delete.append(k)
    for k in to_delete:
      del self._db[k]
    return len(to_delete)