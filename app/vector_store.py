from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.storage import StorageContext
from llama_index.core.indices.loading import load_index_from_storage
import os
import logging
from app.config import VECTOR_STORE_DIR, PDF_PROCESSED_DIR

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        """Initialize the vector store for document retrieval."""
        self.index = None
        self.load_or_create_index()

    def load_or_create_index(self):
        """Load existing index or create a new one if none exists."""
        try:
            if os.path.exists(VECTOR_STORE_DIR) and os.listdir(VECTOR_STORE_DIR):
                logger.info(f"Loading existing index from {VECTOR_STORE_DIR}")
                storage_context = StorageContext.from_defaults(
                    persist_dir=VECTOR_STORE_DIR
                )
                self.index = load_index_from_storage(storage_context)
            else:
                logger.info("No existing index found. Creating new index...")
                self.create_index()
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            logger.info("Creating new index...")
            self.create_index()

    def create_index(self):
        """Create a new index from processed documents."""
        if not os.path.exists(PDF_PROCESSED_DIR) or not os.listdir(PDF_PROCESSED_DIR):
            logger.warning(
                f"No documents found in {PDF_PROCESSED_DIR}. Index creation skipped."
            )
            return

        try:
            documents = SimpleDirectoryReader(PDF_PROCESSED_DIR).load_data()
            self.index = VectorStoreIndex.from_documents(documents)
            self.persist_index()
            logger.info(f"Index created successfully with {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise

    def persist_index(self):
        """Save the index to disk."""
        if self.index:
            self.index.storage_context.persist(persist_dir=VECTOR_STORE_DIR)
            logger.info(f"Index saved to {VECTOR_STORE_DIR}")

    def query(self, query_text):
        """Query the vector store for relevant document chunks."""
        if not self.index:
            logger.error("Cannot query - index is not loaded")
            return "Sorry, the document index is not available right now."

        try:
            query_engine = self.index.as_query_engine()
            response = query_engine.query(query_text)
            return response
        except Exception as e:
            logger.error(f"Error querying index: {e}")
            return f"Error processing query: {str(e)}"

    def refresh_index(self):
        """Refresh the index with the latest documents."""
        logger.info("Refreshing document index...")
        self.create_index()
        return "Index refreshed successfully"
