"""
Tests for the Preferences class and related functionality.
"""
import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from loom.core.preferences import Preferences, PREFS_PREFIX


class TestPreferences:
  """Test cases for Preferences class."""

  def setup_method(self):
    """Set up test fixtures before each test method."""
    # Create a temporary database file for testing
    self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".unqlite")
    self.temp_db.close()
    self.db_path = self.temp_db.name
    self.prefs = Preferences(db_path=self.db_path)

  def teardown_method(self):
    """Clean up after each test method."""
    # Clean up the temporary database file
    try:
      if os.path.exists(self.db_path):
        os.unlink(self.db_path)
    except Exception:
      pass  # File might be locked or already deleted

  def test_init_default_db_path(self):
    """Test Preferences initialization with default database path."""
    with patch('loom.core.preferences.get_database_dir') as mock_get_db_dir:
      mock_get_db_dir.return_value = "/tmp/test_dir"
      prefs = Preferences()
      assert prefs._db is not None

  def test_init_custom_db_path(self):
    """Test Preferences initialization with custom database path."""
    assert self.prefs._db is not None

  def test_k_method(self):
    """Test that _k method adds correct prefix."""
    key = "test_key"
    assert self.prefs._k(key) == f"{PREFS_PREFIX}{key}"

  def test_set_string_value(self):
    """Test setting a string preference."""
    key = "test_string"
    value = "test_value"
    self.prefs.set(key, value)
    
    # Verify it was saved correctly
    stored_value = self.prefs.get(key)
    assert stored_value == value

  def test_set_int_value(self):
    """Test setting an integer preference."""
    key = "test_int"
    value = 42
    self.prefs.set(key, value)
    
    stored_value = self.prefs.get(key)
    assert stored_value == value
    assert isinstance(stored_value, int)

  def test_set_float_value(self):
    """Test setting a float preference."""
    key = "test_float"
    value = 3.14
    self.prefs.set(key, value)
    
    stored_value = self.prefs.get(key)
    assert stored_value == value
    assert isinstance(stored_value, float)

  def test_set_bool_value(self):
    """Test setting a boolean preference."""
    key = "test_bool"
    value = True
    self.prefs.set(key, value)
    
    stored_value = self.prefs.get(key)
    assert stored_value == value
    assert isinstance(stored_value, bool)

  def test_set_list_value(self):
    """Test setting a list preference."""
    key = "test_list"
    value = [1, 2, 3, "four"]
    self.prefs.set(key, value)
    
    stored_value = self.prefs.get(key)
    assert stored_value == value
    assert isinstance(stored_value, list)

  def test_set_dict_value(self):
    """Test setting a dictionary preference."""
    key = "test_dict"
    value = {"name": "test", "count": 5, "enabled": True}
    self.prefs.set(key, value)
    
    stored_value = self.prefs.get(key)
    assert stored_value == value
    assert isinstance(stored_value, dict)

  def test_get_nonexistent_key_returns_default(self):
    """Test getting a non-existent key returns default value."""
    result = self.prefs.get("nonexistent_key", "default_value")
    assert result == "default_value"

  def test_get_nonexistent_key_returns_none(self):
    """Test getting a non-existent key without default returns None."""
    result = self.prefs.get("nonexistent_key")
    assert result is None

  def test_get_with_type_casting_int(self):
    """Test getting a value with integer type casting."""
    key = "test_type_int"
    self.prefs.set(key, "42")
    
    result = self.prefs.get(key, type_=int)
    assert result == 42
    assert isinstance(result, int)

  def test_get_with_type_casting_float(self):
    """Test getting a value with float type casting."""
    key = "test_type_float"
    self.prefs.set(key, "3.14")
    
    result = self.prefs.get(key, type_=float)
    assert result == 3.14
    assert isinstance(result, float)

  def test_get_with_type_casting_bool_true_variants(self):
    """Test getting boolean values with various true string representations."""
    test_cases = ["1", "true", "True", "TRUE", "yes", "Yes", "y", "Y", "on", "ON"]
    
    for i, value in enumerate(test_cases):
      key = f"test_bool_true_{i}"
      # Store as string to test bool casting
      self.prefs._db[self.prefs._k(key)] = json.dumps(value)
      
      result = self.prefs.get(key, type_=bool)
      assert result is True, f"Failed for value: {value}"

  def test_get_with_type_casting_bool_false_variants(self):
    """Test getting boolean values with various false string representations."""
    test_cases = ["0", "false", "False", "FALSE", "no", "No", "n", "N", "off", "OFF"]
    
    for i, value in enumerate(test_cases):
      key = f"test_bool_false_{i}"
      # Store as string to test bool casting
      self.prefs._db[self.prefs._k(key)] = json.dumps(value)
      
      result = self.prefs.get(key, type_=bool)
      assert result is False, f"Failed for value: {value}"

  def test_get_with_type_casting_failure_returns_default(self):
    """Test that type casting failure returns default value."""
    key = "test_type_fail"
    self.prefs.set(key, "not_a_number")
    
    result = self.prefs.get(key, default=99, type_=int)
    assert result == 99

  def test_get_with_non_json_data(self):
    """Test getting data that wasn't JSON-encoded (backward compatibility)."""
    key = "test_non_json"
    raw_value = b"raw_bytes_value"
    self.prefs._db[self.prefs._k(key)] = raw_value
    
    result = self.prefs.get(key)
    # Should return the raw value when JSON parsing fails
    assert result == raw_value

  def test_delete_existing_key(self):
    """Test deleting an existing preference."""
    key = "test_delete"
    self.prefs.set(key, "value")
    
    # Verify it exists
    assert self.prefs.exists(key)
    
    # Delete it
    result = self.prefs.delete(key)
    assert result is True
    assert not self.prefs.exists(key)

  def test_delete_nonexistent_key(self):
    """Test deleting a non-existent preference."""
    result = self.prefs.delete("nonexistent_key")
    assert result is False

  def test_exists_true(self):
    """Test exists method returns True for existing key."""
    key = "test_exists"
    self.prefs.set(key, "value")
    
    assert self.prefs.exists(key) is True

  def test_exists_false(self):
    """Test exists method returns False for non-existent key."""
    assert self.prefs.exists("nonexistent_key") is False

  def test_all_empty(self):
    """Test all method returns empty dict when no preferences exist."""
    result = self.prefs.all()
    assert result == {}

  def test_all_with_preferences(self):
    """Test all method returns all preferences."""
    test_data = {
      "key1": "value1",
      "key2": 42,
      "key3": True,
      "key4": [1, 2, 3],
      "key5": {"nested": "dict"}
    }
    
    for key, value in test_data.items():
      self.prefs.set(key, value)
    
    result = self.prefs.all()
    assert result == test_data

  def test_all_with_non_json_data(self):
    """Test all method handles non-JSON data gracefully."""
    # Set a normal preference
    self.prefs.set("normal_key", "normal_value")
    
    # Add a non-JSON preference directly
    raw_key = "raw_key"
    raw_value = "raw_value"
    self.prefs._db[self.prefs._k(raw_key)] = raw_value
    
    result = self.prefs.all()
    assert "normal_key" in result
    assert "raw_key" in result

  def test_all_filters_non_preference_keys(self):
    """Test that all method only returns keys with preference prefix."""
    # Set a preference
    self.prefs.set("pref_key", "value")
    
    # Add a non-preference key directly
    self.prefs._db["other:key"] = json.dumps("other_value")
    
    result = self.prefs.all()
    assert "pref_key" in result
    assert "key" not in result  # Should not include the non-prefixed key

  def test_clear_empty(self):
    """Test clear method on empty preferences."""
    count = self.prefs.clear()
    assert count == 0

  def test_clear_with_preferences(self):
    """Test clear method removes all preferences."""
    # Add multiple preferences
    for i in range(5):
      self.prefs.set(f"key{i}", f"value{i}")
    
    # Verify they exist
    assert len(self.prefs.all()) == 5
    
    # Clear them
    count = self.prefs.clear()
    assert count == 5
    
    # Verify they're gone
    assert len(self.prefs.all()) == 0

  def test_clear_only_removes_preferences(self):
    """Test that clear only removes preference keys, not other data."""
    # Set a preference
    self.prefs.set("pref_key", "value")
    
    # Add a non-preference key directly
    self.prefs._db["other:key"] = json.dumps("other_value")
    
    # Clear preferences
    count = self.prefs.clear()
    assert count == 1
    
    # Verify non-preference key still exists
    assert "other:key" in self.prefs._db

  def test_multiple_operations_sequence(self):
    """Test a sequence of multiple operations."""
    # Set multiple values
    self.prefs.set("user", "john_doe")
    self.prefs.set("age", 30)
    self.prefs.set("active", True)
    
    # Get and verify
    assert self.prefs.get("user") == "john_doe"
    assert self.prefs.get("age") == 30
    assert self.prefs.get("active") is True
    
    # Update a value
    self.prefs.set("age", 31)
    assert self.prefs.get("age") == 31
    
    # Delete one
    self.prefs.delete("active")
    assert not self.prefs.exists("active")
    
    # Verify others still exist
    all_prefs = self.prefs.all()
    assert len(all_prefs) == 2
    assert "user" in all_prefs
    assert "age" in all_prefs


class TestPreferencesEdgeCases:
  """Test edge cases and error conditions."""

  def setup_method(self):
    """Set up test fixtures before each test method."""
    self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".unqlite")
    self.temp_db.close()
    self.db_path = self.temp_db.name
    self.prefs = Preferences(db_path=self.db_path)

  def teardown_method(self):
    """Clean up after each test method."""
    try:
      if os.path.exists(self.db_path):
        os.unlink(self.db_path)
    except Exception:
      pass

  def test_empty_string_key(self):
    """Test preferences with empty string key."""
    self.prefs.set("", "value")
    assert self.prefs.get("") == "value"

  def test_empty_string_value(self):
    """Test setting empty string as value."""
    self.prefs.set("empty", "")
    assert self.prefs.get("empty") == ""

  def test_none_value(self):
    """Test setting None as value."""
    self.prefs.set("none_key", None)
    assert self.prefs.get("none_key") is None

  def test_unicode_key(self):
    """Test preferences with unicode characters in key."""
    key = "emoji_🚀_test"
    value = "unicode_value"
    self.prefs.set(key, value)
    assert self.prefs.get(key) == value

  def test_unicode_value(self):
    """Test preferences with unicode characters in value."""
    key = "test"
    value = "Hello 世界 🌍"
    self.prefs.set(key, value)
    assert self.prefs.get(key) == value

  def test_very_long_key(self):
    """Test preferences with very long key."""
    key = "a" * 1000
    value = "value"
    self.prefs.set(key, value)
    assert self.prefs.get(key) == value

  def test_very_long_value(self):
    """Test preferences with very long value."""
    key = "long_value"
    value = "x" * 10000
    self.prefs.set(key, value)
    assert self.prefs.get(key) == value

  def test_nested_data_structures(self):
    """Test deeply nested data structures."""
    key = "nested"
    value = {
      "level1": {
        "level2": {
          "level3": {
            "data": [1, 2, {"nested_list": [4, 5, 6]}]
          }
        }
      }
    }
    self.prefs.set(key, value)
    assert self.prefs.get(key) == value

  def test_special_characters_in_key(self):
    """Test keys with special characters."""
    special_keys = [
      "key-with-dashes",
      "key_with_underscores",
      "key.with.dots",
      "key:with:colons",
      "key/with/slashes",
    ]
    
    for key in special_keys:
      self.prefs.set(key, "value")
      assert self.prefs.get(key) == "value", f"Failed for key: {key}"


# Fixtures for common test data
@pytest.fixture
def sample_preferences():
  """Provide sample preference data for tests."""
  return {
    "theme": "dark",
    "font_size": 14,
    "auto_save": True,
    "recent_files": ["/path/to/file1.txt", "/path/to/file2.txt"],
    "window_position": {"x": 100, "y": 200, "width": 800, "height": 600}
  }


@pytest.fixture
def temp_preferences():
  """Provide a temporary Preferences instance for tests."""
  temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".unqlite")
  temp_db.close()
  db_path = temp_db.name
  prefs = Preferences(db_path=db_path)
  
  yield prefs
  
  # Cleanup
  try:
    if os.path.exists(db_path):
      os.unlink(db_path)
  except Exception:
    pass

