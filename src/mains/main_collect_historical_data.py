# src/mains/main_collect_historical.py
import logging

from clients.selenium_client import SeleniumClient
from config import BYMA_COLLECTION, DOWNLOAD_DIR, HISTORICAL_URLS, MONGO_DB_NAME, MONGO_URI
from dao.file_manager_dao import FileManagerDAO
from dao.mongo_manager_dao import MongoManagerDAO
from services.download_service import DownloadService

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting historical data collection service...")

    selenium_client = SeleniumClient(DOWNLOAD_DIR)
    file_manager = FileManagerDAO(DOWNLOAD_DIR)
    mongo_manager = MongoManagerDAO(MONGO_URI, MONGO_DB_NAME, BYMA_COLLECTION)
    service = DownloadService(selenium_client, file_manager, mongo_manager)

    try:
        service.collect_and_store(HISTORICAL_URLS)
    finally:
        selenium_client.quit()
        logger.info("Historical data collection finished.")


if __name__ == "__main__":
    main()
