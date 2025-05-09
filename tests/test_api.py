"""
Test the FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


# Mock the Chatbot class to avoid needing actual dependencies
@pytest.fixture
def mock_chatbot():
    with patch("app.main.Chatbot") as mock:
        # Configure the mock to return predictable responses
        mock_instance = MagicMock()
        mock_instance.get_response.return_value = {
            "answer": "Test answer",
            "sources": "Test sources",
            "response_time": 0.1,
        }
        mock_instance.refresh_knowledge.return_value = "Index refreshed successfully"

        # Make the mock constructor return our configured mock instance
        mock.return_value = mock_instance
        yield mock


def test_root_endpoint():
    """Test the root endpoint returns expected data"""
    with patch("app.main.Chatbot"):
        from app.main import app

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        assert "message" in response.json()
        assert "endpoints" in response.json()


def test_health_endpoint():
    """Test the health endpoint returns healthy status"""
    with patch("app.main.Chatbot"):
        from app.main import app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "timestamp" in response.json()


def test_chat_endpoint(mock_chatbot):
    """Test the chat endpoint returns response from chatbot"""
    from app.main import app

    client = TestClient(app)

    # Test with minimal input
    response = client.post("/chat", json={"query": "test question"})

    assert response.status_code == 200
    assert response.json()["answer"] == "Test answer"
    assert response.json()["sources"] == "Test sources"
    assert response.json()["response_time"] == 0.1

    # Verify the mock was called correctly
    mock_chatbot.return_value.get_response.assert_called_once_with(
        "test question", None
    )


def test_chat_endpoint_with_history(mock_chatbot):
    """Test the chat endpoint with conversation history"""
    from app.main import app

    client = TestClient(app)

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
    mock_chatbot.return_value.get_response.assert_called_once_with(
        "follow-up question", history
    )
