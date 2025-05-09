import schedule
import time
import logging
import threading
import os
from datetime import datetime
from etl.download_pdfs import PDFDownloader
from etl.extract_text import PDFProcessor
from app.vector_store import VectorStore
from app.config import ETL_SCHEDULE_HOUR
from monitor.alerts import alerts

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# URL file path (create one if you want to use it)
URL_FILE = "data/pdf_urls.txt"


class ETLScheduler:
    """Schedules and runs ETL jobs to process PDF documents."""

    def __init__(self, hour=None):
        """
        Initialize the ETL scheduler.

        Args:
            hour (int): Hour of the day to run the ETL job (0-23)
        """
        self.hour = hour or ETL_SCHEDULE_HOUR
        self.vector_store = VectorStore()
        self.stop_event = threading.Event()

    def run_etl_job(self):
        """Run the complete ETL process."""
        try:
            start_time = time.time()
            job_id = datetime.now().strftime("%Y%m%d%H%M%S")
            logger.info(f"Starting ETL job {job_id}")

            # Download new PDFs
            downloader = PDFDownloader()
            if os.path.exists(URL_FILE):
                logger.info(f"Downloading PDFs from URL file: {URL_FILE}")
                downloaded_files = downloader.download_from_file(URL_FILE)
            else:
                logger.info(f"URL file not found: {URL_FILE}")
                downloaded_files = []

            # Process downloaded PDFs
            processor = PDFProcessor()
            processed_files = processor.process_all_pdfs()

            # Generate metadata
            if processed_files:
                metadata_file = processor.generate_metadata_csv(processed_files)
                logger.info(f"Generated metadata file: {metadata_file}")

            # Refresh vector store
            if processed_files:
                logger.info("Refreshing vector store with new documents")
                self.vector_store.refresh_index()

            # Log job completion
            elapsed_time = time.time() - start_time
            logger.info(f"ETL job {job_id} completed in {elapsed_time:.2f} seconds")

            # Send alert about job completion
            alerts.send_alert(
                title="ETL Job Completed",
                message=f"ETL job {job_id} completed successfully",
                level="info",
                downloaded=len(downloaded_files),
                processed=len(processed_files),
                elapsed_time=f"{elapsed_time:.2f}s",
            )

            return True

        except Exception as e:
            logger.error(f"Error in ETL job: {str(e)}")

            # Send alert about job failure
            alerts.send_error_alert(
                error_type="ETL Job Failure",
                error_message=str(e),
                details={"job_id": job_id if "job_id" in locals() else "unknown"},
            )

            return False

    def start_scheduler(self):
        """Start the scheduler to run ETL jobs at the specified hour."""
        logger.info(f"Scheduling ETL job to run daily at {self.hour}:00")

        # Schedule the job to run daily at the specified hour
        schedule.every().day.at(f"{self.hour:02d}:00").do(self.run_etl_job)

        # Run the scheduler in a loop
        while not self.stop_event.is_set():
            schedule.run_pending()
            time.sleep(60)  # Check every minute

        logger.info("ETL scheduler stopped")

    def start(self):
        """Start the scheduler in a background thread."""
        thread = threading.Thread(target=self.start_scheduler)
        thread.daemon = True
        thread.start()
        logger.info("ETL scheduler started in background thread")
        return thread

    def stop(self):
        """Stop the scheduler."""
        self.stop_event.set()
        logger.info("ETL scheduler stop requested")

    def run_now(self):
        """Run the ETL job immediately."""
        logger.info("Running ETL job now")
        return self.run_etl_job()


# Example usage
if __name__ == "__main__":
    # Run scheduler in main thread for testing
    scheduler = ETLScheduler()

    # Run immediately for testing
    scheduler.run_now()

    # Or start the scheduler
    # scheduler.start_scheduler()
