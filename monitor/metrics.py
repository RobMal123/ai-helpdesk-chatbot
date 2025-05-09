import time
import logging
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import threading
from app.config import ENABLE_METRICS
import atexit

logger = logging.getLogger(__name__)

# Define metrics
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["endpoint", "method", "status"],
)
RESPONSE_TIME = Histogram(
    "api_response_time_seconds", "Response time in seconds", ["endpoint"]
)
TOKEN_USAGE = Counter("token_usage_total", "Total number of tokens used", ["model"])
ERROR_COUNT = Counter("error_count_total", "Total number of errors", ["type"])
ACTIVE_USERS = Gauge("active_users", "Number of active users")
PDF_COUNT = Gauge("pdf_count", "Number of PDF documents indexed")
VECTOR_STORE_SIZE = Gauge("vector_store_size_bytes", "Size of vector store in bytes")

# Quality metrics
ANSWER_QUALITY = Gauge("answer_quality", "Quality score of AI responses (0-100)")
CONTEXT_RELEVANCE = Histogram(
    "context_relevance", "Relevance score of retrieved contexts (0-1)"
)


class MetricsServer:
    """Manages Prometheus metrics server and collection."""

    def __init__(self, port=8001):
        self.port = port
        self.server_thread = None
        self._server_started = False

        if ENABLE_METRICS:
            self.start_server()
            # Register shutdown handler
            atexit.register(self.shutdown)

    def start_server(self):
        """Start the Prometheus metrics server in a separate thread."""
        if self._server_started:
            return

        def server_thread():
            logger.info(f"Starting Prometheus metrics server on port {self.port}")
            start_http_server(self.port)

        self.server_thread = threading.Thread(target=server_thread)
        self.server_thread.daemon = True
        self.server_thread.start()
        self._server_started = True
        logger.info("Metrics server started")

    def shutdown(self):
        """Shutdown handler for clean exit."""
        logger.info("Shutting down metrics server")
        # Prometheus client doesn't provide a direct shutdown method
        # The daemon thread will exit when the program exits

    def record_request(self, endpoint, method, status, duration):
        """Record API request metrics."""
        if not ENABLE_METRICS:
            return

        REQUEST_COUNT.labels(endpoint=endpoint, method=method, status=status).inc()
        RESPONSE_TIME.labels(endpoint=endpoint).observe(duration)
        logger.debug(f"Recorded request: {endpoint} {method} {status} {duration:.4f}s")

    def record_token_usage(self, count, model="gemini-2.0-flash-lite"):
        """Record token usage metrics."""
        if not ENABLE_METRICS and count > 0:
            TOKEN_USAGE.labels(model=model).inc(count)
            logger.debug(f"Recorded token usage: {count} tokens for model {model}")

    def record_error(self, error_type):
        """Record error metrics."""
        if not ENABLE_METRICS:
            return

        ERROR_COUNT.labels(type=error_type).inc()
        logger.debug(f"Recorded error: {error_type}")

    def update_pdf_count(self, count):
        """Update PDF document count gauge."""
        if not ENABLE_METRICS:
            return

        PDF_COUNT.set(count)
        logger.debug(f"Updated PDF count: {count}")

    def update_vector_store_size(self, size_bytes):
        """Update vector store size gauge."""
        if not ENABLE_METRICS:
            return

        VECTOR_STORE_SIZE.set(size_bytes)
        logger.debug(f"Updated vector store size: {size_bytes} bytes")

    def update_answer_quality(self, score):
        """Update answer quality gauge (0-100)."""
        if not ENABLE_METRICS:
            return

        ANSWER_QUALITY.set(score)
        logger.debug(f"Updated answer quality score: {score}")

    def record_context_relevance(self, score):
        """Record context relevance score (0-1)."""
        if not ENABLE_METRICS and 0 <= score <= 1:
            CONTEXT_RELEVANCE.observe(score)
            logger.debug(f"Recorded context relevance: {score}")


# Singleton instance
metrics = MetricsServer()


# Middleware for FastAPI to record request metrics
async def metrics_middleware(request, call_next):
    start_time = time.time()

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        metrics.record_error(type(e).__name__)
        raise
    finally:
        duration = time.time() - start_time
        metrics.record_request(
            endpoint=request.url.path,
            method=request.method,
            status=status_code if "status_code" in locals() else 500,
            duration=duration,
        )

    return response
