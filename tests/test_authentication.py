import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create a dummy get_credentials function for testing
def get_credentials():
    import os
    from oauth2client.file import Storage

    credential_path = os.path.join(".auth","credentials.json")
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid or getattr(credentials, 'access_token_expired', False):
        print("Credentials not found or invalid.")
        return False
    else:
        print("Credentials fetched successfully.")
        return credentials

# Mocking path for auth storage
TEST_CREDENTIAL_PATH = ".auth/test_credentials.json"

def setup_module(module):
    """Ensure the test credentials directory exists."""
    os.makedirs(".auth", exist_ok=True)

def teardown_module(module):
    """Clean up test credentials after tests."""
    if os.path.exists(TEST_CREDENTIAL_PATH):
        os.remove(TEST_CREDENTIAL_PATH)

@pytest.fixture
def mock_storage_path(monkeypatch):
    """Fixture to temporarily replace the credential storage path."""
    monkeypatch.setattr('os.path.join', lambda *args: TEST_CREDENTIAL_PATH)

def test_get_credentials_no_credentials(mock_storage_path):
    """Test get_credentials() when no credentials exist."""
    # Ensure no credentials file exists
    if os.path.exists(TEST_CREDENTIAL_PATH):
        os.remove(TEST_CREDENTIAL_PATH)
    
    # Use patch to simulate Storage().get() returning None
    with patch('oauth2client.file.Storage.get', return_value=None):
        result = get_credentials()
        assert result is False, "Should return False when no credentials exist"

def test_get_credentials_invalid_credentials(mock_storage_path):
    """Test get_credentials() with invalid credentials."""
    # Create a mock credentials object
    mock_credentials = MagicMock()
    mock_credentials.invalid = True
    
    # Use patch to simulate Storage().get() returning invalid credentials
    with patch('oauth2client.file.Storage.get', return_value=mock_credentials):
        result = get_credentials()
        assert result is False, "Should return False for invalid credentials"

def test_get_credentials_valid_credentials(mock_storage_path):
    """Test get_credentials() with valid credentials."""
    # Create a mock credentials object
    mock_credentials = MagicMock()
    mock_credentials.invalid = False
    mock_credentials.access_token_expired = False
    
    # Use patch to simulate Storage().get() returning valid credentials
    with patch('oauth2client.file.Storage.get', return_value=mock_credentials):
        result = get_credentials()
        assert result is not False, "Should return credentials when valid"
        assert result == mock_credentials, "Should return the fetched credentials"

def test_get_credentials_expired_token(mock_storage_path):
    """Test get_credentials() with expired access token."""
    # Create a mock credentials object with expired access token
    mock_credentials = MagicMock()
    mock_credentials.invalid = False
    mock_credentials.access_token_expired = True
    
    # Use patch to simulate Storage().get() returning expired credentials
    with patch('oauth2client.file.Storage.get', return_value=mock_credentials):
        result = get_credentials()
        assert result is False, "Should return False for expired credentials"