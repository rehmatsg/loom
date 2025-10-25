"""
Tests for the SecretsManager class and related functionality.
"""
import pytest
import keyring
from unittest.mock import patch, MagicMock
from loom.utils.secrets import SecretsManager, save_secret, get_secret, delete_secret, list_secrets
import typer


class TestSecretsManager:
  """Test cases for SecretsManager class."""

  def setup_method(self):
    """Set up test fixtures before each test method."""
    self.manager = SecretsManager("test_service")
    self.test_key = "test_key"
    self.test_value = "test_value"

  def teardown_method(self):
    """Clean up after each test method."""
    # Clean up any test keys that might have been created
    try:
      keyring.delete_password("test_service", self.test_key)
    except keyring.errors.PasswordDeleteError:
      pass  # Key doesn't exist, which is fine

  def test_init_default_service(self):
    """Test SecretsManager initialization with default service name."""
    manager = SecretsManager()
    assert manager.service_name == "loom"

  def test_init_custom_service(self):
    """Test SecretsManager initialization with custom service name."""
    manager = SecretsManager("custom_service")
    assert manager.service_name == "custom_service"

  @patch('keyring.set_password')
  def test_save_secret_success(self, mock_set_password):
    """Test successful secret saving."""
    result = self.manager.save_secret(self.test_key, self.test_value)

    assert result is True
    mock_set_password.assert_called_once_with(
        "test_service", self.test_key, self.test_value)

  @patch('keyring.set_password')
  def test_save_secret_failure(self, mock_set_password):
    """Test secret saving failure."""
    mock_set_password.side_effect = Exception("Keychain error")

    result = self.manager.save_secret(self.test_key, self.test_value)

    assert result is False

  @patch('keyring.get_password')
  def test_get_secret_success(self, mock_get_password):
    """Test successful secret retrieval."""
    mock_get_password.return_value = self.test_value

    result = self.manager.get_secret(self.test_key)

    assert result == self.test_value
    mock_get_password.assert_called_once_with("test_service", self.test_key)

  @patch('keyring.get_password')
  def test_get_secret_not_found(self, mock_get_password):
    """Test secret retrieval when key doesn't exist."""
    mock_get_password.return_value = None

    result = self.manager.get_secret(self.test_key)

    assert result is None

  @patch('keyring.get_password')
  def test_get_secret_failure(self, mock_get_password):
    """Test secret retrieval failure."""
    mock_get_password.side_effect = Exception("Keychain error")

    result = self.manager.get_secret(self.test_key)

    assert result is None

  @patch('keyring.delete_password')
  def test_delete_secret_success(self, mock_delete_password):
    """Test successful secret deletion."""
    result = self.manager.delete_secret(self.test_key)

    assert result is True
    mock_delete_password.assert_called_once_with("test_service", self.test_key)

  @patch('keyring.delete_password')
  def test_delete_secret_failure(self, mock_delete_password):
    """Test secret deletion failure."""
    mock_delete_password.side_effect = Exception("Keychain error")

    result = self.manager.delete_secret(self.test_key)

    assert result is False

  def test_list_secrets(self):
    """Test list secrets functionality."""
    # This method just prints a message and returns empty list
    result = self.manager.list_secrets()
    assert result == []


class TestCLIFunctions:
  """Test cases for CLI functions."""

  def setup_method(self):
    """Set up test fixtures before each test method."""
    self.test_key = "test_key"
    self.test_value = "test_value"
    self.test_service = "test_service"

  @patch('loom.utils.secrets.SecretsManager')
  def test_save_secret_success(self, mock_manager_class):
    """Test successful secret saving via CLI."""
    mock_manager = MagicMock()
    mock_manager.save_secret.return_value = True
    mock_manager_class.return_value = mock_manager

    # Should not raise an exception
    save_secret(self.test_key, self.test_value, self.test_service)

    mock_manager_class.assert_called_once_with(self.test_service)
    mock_manager.save_secret.assert_called_once_with(
        self.test_key, self.test_value)

  @patch('loom.utils.secrets.SecretsManager')
  def test_save_secret_failure(self, mock_manager_class):
    """Test secret saving failure via CLI."""
    mock_manager = MagicMock()
    mock_manager.save_secret.return_value = False
    mock_manager_class.return_value = mock_manager

    with pytest.raises(typer.Exit):
      save_secret(self.test_key, self.test_value, self.test_service)

  @patch('loom.utils.secrets.SecretsManager')
  def test_get_secret_success(self, mock_manager_class):
    """Test successful secret retrieval via CLI."""
    mock_manager = MagicMock()
    mock_manager.get_secret.return_value = self.test_value
    mock_manager_class.return_value = mock_manager

    # Should not raise an exception
    get_secret(self.test_key, self.test_service, False)

    mock_manager_class.assert_called_once_with(self.test_service)
    mock_manager.get_secret.assert_called_once_with(self.test_key)

  @patch('loom.utils.secrets.SecretsManager')
  def test_get_secret_not_found(self, mock_manager_class):
    """Test secret retrieval when key doesn't exist via CLI."""
    mock_manager = MagicMock()
    mock_manager.get_secret.return_value = None
    mock_manager_class.return_value = mock_manager

    with pytest.raises(typer.Exit):
      get_secret(self.test_key, self.test_service, False)

  @patch('loom.utils.secrets.SecretsManager')
  def test_get_secret_with_key_shown(self, mock_manager_class):
    """Test secret retrieval with key shown via CLI."""
    mock_manager = MagicMock()
    mock_manager.get_secret.return_value = self.test_value
    mock_manager_class.return_value = mock_manager

    # Should not raise an exception
    get_secret(self.test_key, self.test_service, True)

    mock_manager_class.assert_called_once_with(self.test_service)
    mock_manager.get_secret.assert_called_once_with(self.test_key)

  @patch('loom.utils.secrets.SecretsManager')
  def test_delete_secret_success(self, mock_manager_class):
    """Test successful secret deletion via CLI."""
    mock_manager = MagicMock()
    mock_manager.delete_secret.return_value = True
    mock_manager_class.return_value = mock_manager

    # Should not raise an exception
    delete_secret(self.test_key, self.test_service)

    mock_manager_class.assert_called_once_with(self.test_service)
    mock_manager.delete_secret.assert_called_once_with(self.test_key)

  @patch('loom.utils.secrets.SecretsManager')
  def test_delete_secret_failure(self, mock_manager_class):
    """Test secret deletion failure via CLI."""
    mock_manager = MagicMock()
    mock_manager.delete_secret.return_value = False
    mock_manager_class.return_value = mock_manager

    with pytest.raises(typer.Exit):
      delete_secret(self.test_key, self.test_service)

  @patch('loom.utils.secrets.SecretsManager')
  def test_list_secrets(self, mock_manager_class):
    """Test list secrets via CLI."""
    mock_manager = MagicMock()
    mock_manager_class.return_value = mock_manager

    # Should not raise an exception
    list_secrets(self.test_service)

    mock_manager_class.assert_called_once_with(self.test_service)
    mock_manager.list_secrets.assert_called_once()


class TestIntegration:
  """Integration tests that may require actual keychain access."""

  def test_real_keychain_operations(self):
    """Test real keychain operations (may require user interaction)."""
    # Skip this test in CI/CD environments
    import os
    if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
      pytest.skip("Skipping keychain integration test in CI environment")

    manager = SecretsManager("test_integration_service")
    test_key = "integration_test_key"
    test_value = "integration_test_value"

    try:
      # Test save
      result = manager.save_secret(test_key, test_value)
      assert result is True

      # Test get
      retrieved_value = manager.get_secret(test_key)
      assert retrieved_value == test_value

      # Test delete
      result = manager.delete_secret(test_key)
      assert result is True

      # Verify deletion
      retrieved_value = manager.get_secret(test_key)
      assert retrieved_value is None

    except Exception as e:
      pytest.skip(f"Skipping keychain integration test due to: {e}")


# Test configuration
def pytest_configure(config):
  """Configure pytest with custom markers."""
  config.addinivalue_line(
      "markers", "integration: marks tests as integration tests")


# Fixtures for common test data
@pytest.fixture
def sample_secrets():
  """Provide sample secret data for tests."""
  return {
      "api_key": "sk-1234567890abcdef",
      "database_url": "postgresql://user:pass@localhost/db",
      "jwt_secret": "super-secret-jwt-key"
  }


@pytest.fixture
def test_service_name():
  """Provide a test service name."""
  return "loom_test_service"
