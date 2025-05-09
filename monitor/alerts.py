import logging
import requests
import json
from datetime import datetime
from app.config import DISCORD_WEBHOOK_URL

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages alerts through Discord webhooks."""

    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or DISCORD_WEBHOOK_URL

    def send_alert(self, title, message, level="info", **kwargs):
        """
        Send an alert to Discord.

        Args:
            title (str): Alert title
            message (str): Alert message
            level (str): Alert level ('info', 'warning', 'error', 'critical')
            **kwargs: Additional fields to include in the alert
        """
        if not self.webhook_url:
            logger.warning("Discord webhook URL not configured, alert not sent")
            return False

        # Map alert levels to colors
        color_map = {
            "info": 0x3498DB,  # Blue
            "warning": 0xF1C40F,  # Yellow
            "error": 0xE74C3C,  # Red
            "critical": 0x9B59B6,  # Purple
        }

        color = color_map.get(level.lower(), 0x95A5A6)  # Default: gray

        # Create embed for Discord
        embed = {
            "title": title,
            "description": message,
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "footer": {"text": f"AI Helpdesk Chatbot - Alert Level: {level.upper()}"},
            "fields": [],
        }

        # Add additional fields from kwargs
        for key, value in kwargs.items():
            embed["fields"].append({"name": key, "value": str(value), "inline": True})

        payload = {"username": "AI Helpdesk Monitor", "embeds": [embed]}

        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            logger.info(f"Alert sent to Discord: {title}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Discord alert: {str(e)}")
            return False

    def send_quality_alert(self, score, threshold, example_query, example_response):
        """
        Send an alert when response quality drops below a threshold.

        Args:
            score (float): Quality score (0-100)
            threshold (float): Alert threshold
            example_query (str): Example problematic query
            example_response (str): Example problematic response
        """
        if score < threshold:
            level = "warning" if score > threshold * 0.5 else "error"
            return self.send_alert(
                title="Response Quality Alert",
                message=f"Response quality score has dropped to {score:.1f}, below threshold of {threshold}.",
                level=level,
                example_query=example_query[:1000],  # Truncate if too long
                example_response=example_response[:1000],  # Truncate if too long
            )
        return False

    def send_error_alert(self, error_type, error_message, details=None):
        """
        Send an alert for critical system errors.

        Args:
            error_type (str): Type of error
            error_message (str): Error message
            details (dict): Additional error details
        """
        return self.send_alert(
            title=f"System Error: {error_type}",
            message=error_message,
            level="error",
            **(details or {}),
        )

    def send_usage_alert(self, metric_name, current_value, threshold, unit=""):
        """
        Send an alert when a usage metric exceeds threshold.

        Args:
            metric_name (str): Name of the metric
            current_value (float): Current value
            threshold (float): Alert threshold
            unit (str): Unit of measurement
        """
        if current_value > threshold:
            return self.send_alert(
                title=f"Usage Alert: {metric_name}",
                message=f"{metric_name} has reached {current_value}{unit}, exceeding threshold of {threshold}{unit}.",
                level="warning",
                current_value=f"{current_value}{unit}",
                threshold=f"{threshold}{unit}",
            )
        return False


# Singleton instance
alerts = AlertManager()
