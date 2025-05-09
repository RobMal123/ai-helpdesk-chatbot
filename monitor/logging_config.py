import logging
import logging.handlers
import os
import json
from datetime import datetime
from app.config import LOG_LEVEL

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)


# Define log format with extra fields for structured logging
class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName,
        }

        # Add exception info if available
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Add extra fields if available
        if hasattr(record, "extra"):
            log_record.update(record.extra)

        return json.dumps(log_record)


def configure_logging():
    """Configure application-wide logging."""
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))

    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    root_logger.addHandler(console_handler)

    # Rotating file handler for production logs
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
    )
    file_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(file_handler)

    # Create specific logger for chatbot metrics
    metrics_logger = logging.getLogger("chatbot.metrics")
    metrics_file = logging.handlers.RotatingFileHandler(
        "logs/metrics.log", maxBytes=10485760, backupCount=5
    )
    metrics_file.setFormatter(CustomFormatter())
    metrics_logger.addHandler(metrics_file)

    logging.info("Logging configured successfully")

    return root_logger
