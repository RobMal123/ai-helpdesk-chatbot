"""
Test the config module
"""

import os
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


def test_environment_variables():
    """Test that environment variables are loaded correctly"""
    with patch.dict(os.environ, TEST_ENV):
        # Import here to ensure environment variables are mocked
        from app.config import GEMINI_API_KEY, GEMINI_MODEL, APP_HOST, APP_PORT, DEBUG

        assert GEMINI_API_KEY == "test_api_key"
        assert GEMINI_MODEL == "test-model"
        assert APP_HOST == "127.0.0.1"
        assert APP_PORT == 8000
        assert DEBUG is True


def test_data_directories():
    """Test that data directories are created"""
    with patch.dict(os.environ, TEST_ENV):
        # Import here to ensure environment variables are mocked
        from app.config import PDF_SOURCE_DIR, PDF_PROCESSED_DIR, VECTOR_STORE_DIR

        # Just make sure these variables exist
        assert isinstance(PDF_SOURCE_DIR, str)
        assert isinstance(PDF_PROCESSED_DIR, str)
        assert isinstance(VECTOR_STORE_DIR, str)
