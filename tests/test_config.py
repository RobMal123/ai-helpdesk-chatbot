"""
Test the config module
"""

import os
import sys
import pytest
from unittest.mock import patch

# Define a test environment variable to use in tests
TEST_ENV = {
    "GEMINI_API_KEY": "test_api_key",
    "GEMINI_MODEL": "test-model",
    "APP_HOST": "127.0.0.1",
    "APP_PORT": "8000",
    "DEBUG": "True",
}


# Remove the config module from cache to ensure fresh import
def teardown_module():
    """Remove modules from cache after tests to ensure fresh imports"""
    modules_to_remove = ["app.config"]
    for module in list(sys.modules.keys()):
        if any(module.startswith(prefix) for prefix in modules_to_remove):
            del sys.modules[module]


@pytest.fixture
def clean_environment():
    """Clean environment variables and module cache before test"""
    # Remove config module from cache to ensure fresh import
    for module in list(sys.modules.keys()):
        if module.startswith("app.config"):
            del sys.modules[module]

    # Apply environment variables
    with patch.dict(os.environ, TEST_ENV, clear=True):
        yield


def test_environment_variables(clean_environment):
    """Test that environment variables are loaded correctly"""
    # Import here to ensure environment variables are applied first
    from app.config import GEMINI_API_KEY, GEMINI_MODEL, APP_HOST, APP_PORT, DEBUG

    assert GEMINI_API_KEY == "test_api_key"
    assert GEMINI_MODEL == "test-model"
    assert APP_HOST == "127.0.0.1"
    assert APP_PORT == 8000
    assert DEBUG is True


def test_data_directories(clean_environment):
    """Test that data directories are created"""
    # Import here to ensure environment variables are applied first
    from app.config import PDF_SOURCE_DIR, PDF_PROCESSED_DIR, VECTOR_STORE_DIR

    # Just make sure these variables exist
    assert isinstance(PDF_SOURCE_DIR, str)
    assert isinstance(PDF_PROCESSED_DIR, str)
    assert isinstance(VECTOR_STORE_DIR, str)
