# src/mains/main_collect_feeds.py
import logging.config

from config import MONGO_DB_NAME, MONGO_URI, RSS_FEEDS
from dao.mongo_manager_dao import MongoManagerDAO
from logging_config import LOGGING_CONFIG
from services.rss_collector_service import RSSCollectorService

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting RSS feed collection service...")

    # DAO is now generic - no collection_name in constructor
    mongo_manager = MongoManagerDAO(MONGO_URI, MONGO_DB_NAME)
    rss_service = RSSCollectorService(mongo_manager)

    # Optional: pass hours_threshold as parameter (default is 6)
    rss_service.fetch_and_store(RSS_FEEDS, hours_threshold=6)

    logger.info("RSS feed collection finished.")


if __name__ == "__main__":
    main()
