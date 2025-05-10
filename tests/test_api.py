"""
Test the FastAPI endpoints
"""

import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
from prometheus_client import REGISTRY, CollectorRegistry

# Mock environment variables
TEST_ENV = {
    "GEMINI_API_KEY": "test_api_key",
    "GEMINI_MODEL": "test-model",
    "APP_HOST": "127.0.0.1",
    "APP_PORT": "8000",
    "DEBUG": "True",
}


# Remove modules from cache to ensure fresh imports
def teardown_module():
    """Remove modules from cache after tests to ensure fresh imports"""
    modules_to_remove = ["app.main", "app.chatbot", "app.config", "app.vector_store"]
    for module in list(sys.modules.keys()):
        if any(module.startswith(prefix) for prefix in modules_to_remove):
            del sys.modules[module]


@pytest.fixture(scope="function")
def clean_environment():
    """Clean environment variables and module cache before test"""
    # Remove modules from cache to ensure fresh import
    for module in list(sys.modules.keys()):
        if module.startswith("app."):
            del sys.modules[module]

    # Patch Prometheus registry
    original_registry = REGISTRY._names_to_collectors.copy()

    # Apply environment variables
    with patch.dict(os.environ, TEST_ENV, clear=True):
        yield

    # Restore Prometheus registry state
    REGISTRY._names_to_collectors = original_registry


# Create a mock chatbot that returns predictable responses
@pytest.fixture
def mock_chatbot_instance():
    mock = MagicMock()
    mock.get_response.return_value = {
        "answer": "Test answer",
        "sources": "Test sources",
        "response_time": 0.1,
    }
    mock.refresh_knowledge.return_value = "Index refreshed successfully"
    return mock


# Mock the get_chatbot function to return our mock instance
@pytest.fixture
def override_get_chatbot(mock_chatbot_instance, clean_environment):
    # Import here after environment is set up
    with patch("prometheus_client.Histogram"):
        from app.main import app, get_chatbot

        # Override the get_chatbot dependency
        app.dependency_overrides[get_chatbot] = lambda: mock_chatbot_instance

        # Return app with dependency override
        yield app

    # Clean up after test
    app.dependency_overrides.clear()


def test_root_endpoint(clean_environment):
    """Test the root endpoint returns expected data"""
    # Import after environment is set up
    with patch("prometheus_client.Histogram"):
        from app.main import app

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        assert "message" in response.json()
        assert "endpoints" in response.json()


def test_health_endpoint(clean_environment):
    """Test the health endpoint returns healthy status"""
    # Import after environment is set up
    with patch("prometheus_client.Histogram"):
        from app.main import app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "timestamp" in response.json()


def test_chat_endpoint(override_get_chatbot, mock_chatbot_instance):
    """Test the chat endpoint returns response from chatbot"""
    client = TestClient(override_get_chatbot)

    # Test with minimal input
    response = client.post("/chat", json={"query": "test question"})

    assert response.status_code == 200
    assert response.json()["answer"] == "Test answer"
    assert response.json()["sources"] == "Test sources"
    assert response.json()["response_time"] == 0.1

    # Verify the mock was called correctly
    mock_chatbot_instance.get_response.assert_called_once_with("test question", None)


def test_chat_endpoint_with_history(override_get_chatbot, mock_chatbot_instance):
    """Test the chat endpoint with conversation history"""
    client = TestClient(override_get_chatbot)

    # Test with conversation history
    history = [
        {"role": "user", "content": "previous question"},
        {"role": "assistant", "content": "previous answer"},
    ]

    response = client.post(
        "/chat", json={"query": "follow-up question", "conversation_history": history}
    )

    assert response.status_code == 200

    # Verify the history was passed correctly
    mock_chatbot_instance.get_response.assert_called_once_with(
        "follow-up question", history
    )
