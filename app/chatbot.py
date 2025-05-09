import logging
import time
from app.vector_store import VectorStore
from app.config import GEMINI_API_KEY, GEMINI_MODEL
import google.generativeai as genai
from prometheus_client import Histogram

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Setup logging
logger = logging.getLogger(__name__)

# Prometheus metrics for response time
RESPONSE_TIME = Histogram(
    "chatbot_response_time_seconds", "Time spent generating chatbot response"
)
TOKEN_USAGE = Histogram("chatbot_token_usage", "Number of tokens used per request")


class Chatbot:
    def __init__(self):
        """Initialize the chatbot with vector store for RAG."""
        self.vector_store = VectorStore()
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        logger.info("Chatbot initialized with RAG capabilities using Gemini")

    @RESPONSE_TIME.time()
    def get_response(self, query, conversation_history=None):
        """Generate a response to the user query using RAG."""
        if conversation_history is None:
            conversation_history = []

        start_time = time.time()
        logger.info(f"Processing query: {query}")

        try:
            # Get relevant context from vector store
            rag_context = self.vector_store.query(query)
            context_str = str(rag_context)

            # Prepare chat history for Gemini
            # Convert from OpenAI format to Gemini chat format
            gemini_messages = []

            # Add system message with context
            system_prompt = f"You are a helpful assistant answering questions based on the following information: {context_str}. If you don't know the answer based on this information, say so."

            # Start a new chat with the system prompt
            chat = self.model.start_chat(history=[])

            # Add conversation history
            for message in conversation_history[
                -5:
            ]:  # Only use last 5 messages for context
                role = message.get("role", "")
                content = message.get("content", "")

                if role == "user":
                    gemini_messages.append({"role": "user", "parts": [content]})
                elif role == "assistant":
                    gemini_messages.append({"role": "model", "parts": [content]})

            # Add current query with context
            prompt = f"Context: {context_str}\n\nQuestion: {query}"

            # Generate response using Gemini
            response = chat.send_message(prompt)

            # Extract token usage - Gemini doesn't provide token count directly
            # We'll estimate based on characters
            estimated_tokens = len(prompt) / 4  # Rough estimate
            TOKEN_USAGE.observe(estimated_tokens)
            logger.info(f"Estimated token usage: {estimated_tokens}")

            answer = response.text

            # Log response time
            elapsed_time = time.time() - start_time
            logger.info(f"Response generated in {elapsed_time:.2f} seconds")

            return {
                "answer": answer,
                "sources": str(rag_context.get_formatted_sources())
                if hasattr(rag_context, "get_formatted_sources")
                else "",
                "response_time": elapsed_time,
            }

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "answer": "I'm sorry, I encountered an error processing your request.",
                "error": str(e),
                "response_time": time.time() - start_time,
            }

    def refresh_knowledge(self):
        """Refresh the knowledge base with latest documents."""
        return self.vector_store.refresh_index()
