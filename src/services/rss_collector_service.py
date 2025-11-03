import logging
from datetime import datetime, timedelta

import feedparser
from bs4 import BeautifulSoup

from src.config import FEEDS_UPDATE_HOURS, RSS_COLLECTION, RSS_FEEDS
from src.dao.mongo_manager_dao import MongoManagerDAO

logger = logging.getLogger(__name__)

# ---------------- Helper Functions ----------------


def get_image_url(entry: dict) -> str | None:
    """
    Extract main image URL from feed entry
    Priority order:
    1. enclosures
    2. media_content
    3. first <img> in content/summary/description
    """
    # Check enclosures
    if "enclosures" in entry and len(entry.enclosures) > 0:
        url = entry.enclosures[0].get("href")
        if url:
            return url

    # Check media_content
    if "media_content" in entry and len(entry.media_content) > 0:
        url = entry.media_content[0].get("url")
        if url:
            return url

    # Parse HTML content for images
    content_html = entry.get("content", [{}])[0].get("value") or entry.get("summary", "") or entry.get("description", "")

    if content_html:
        soup = BeautifulSoup(content_html, "html.parser")
        img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            return img_tag["src"]

    return None


def html_to_text(html: str) -> str:
    """Convert HTML to clean text with proper spacing"""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ").strip()


# ---------------- Main RSS Service ----------------


class RSSCollectorService:
    def __init__(self, mongo_manager: MongoManagerDAO):
        self.mongo_manager = mongo_manager

    def fetch_and_store(self, rss_feeds: list = RSS_FEEDS, hours_threshold: int = FEEDS_UPDATE_HOURS):
        """Main method to fetch RSS feeds and store in database with execution tracking"""
        logger.info(f"Starting RSS feed collection process with {hours_threshold}h threshold")

        # 1. Create execution log record
        start_time = datetime.now()
        execution_record = {
            "process_name": "main_collect_feeds",
            "execution_time": start_time,
            "status": "running",
            "parameters": {"hours_threshold": hours_threshold},
            "execution_duration": None,
        }

        execution_id = self.mongo_manager.insert_one(execution_record, "process_execution_logs")
        logger.info(f"Created execution record with ID: {execution_id}")

        try:
            # 2. Check last successful execution
            last_success = self.mongo_manager.find_one(
                {"process_name": "main_collect_feeds", "status": "success"},
                "process_execution_logs",
            )

            if last_success:
                last_execution_time = last_success["execution_time"]
                time_since_last = start_time - last_execution_time

                if time_since_last < timedelta(hours=hours_threshold):
                    # Update record as skipped
                    self.mongo_manager.update_one(
                        {"_id": execution_id},
                        {
                            "$set": {
                                "status": "skipped",
                                "execution_duration": (datetime.now() - start_time).total_seconds(),
                            }
                        },
                        "process_execution_logs",
                    )
                    logger.info(f"Skipping execution - Last successful run was {time_since_last} ago")
                    return

            # 3. Remove old feeds from today's executions
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_executions = self.mongo_manager.find(
                {"process_name": "main_collect_feeds", "execution_time": {"$gte": today_start}},
                "process_execution_logs",
            )

            today_execution_ids = [execution["_id"] for execution in today_executions]

            if today_execution_ids:
                deleted_count = self.mongo_manager.delete_many({"execution_id": {"$in": today_execution_ids}}, RSS_COLLECTION)
                logger.info(f"Deleted {deleted_count} old feeds from today's executions")

            # 4. Process feeds and associate with execution_id
            all_items = []

            for rss_feed in rss_feeds:
                feed = feedparser.parse(rss_feed["url"])
                items = []

                for entry in feed.entries:
                    # Extract image URL
                    image_url = get_image_url(entry)

                    # Build item dictionary with execution_id
                    item = {
                        "sourceId": rss_feed["sourceId"],
                        "source_name": rss_feed["name"],
                        "title": html_to_text(entry.get("title", "")),
                        "summary": html_to_text(entry.get("summary", "")),
                        "content": html_to_text(entry.get("content", [{}])[0].get("value", "")),
                        "description": html_to_text(entry.get("description", "")),
                        "link": entry.get("link"),
                        "pubDate": entry.get("published", str(datetime.now())),
                        "source": rss_feed["url"],
                        "image_url": image_url,
                        "author": entry.get("author"),
                        "tags": [tag.term for tag in entry.get("tags", [])],
                        "execution_id": execution_id,  # Associate with current execution
                    }

                    items.append(item)

                if items:
                    all_items.extend(items)
                    logger.info(f"Collected {len(items)} items from {rss_feed['url']}")
                else:
                    logger.warning(f"No items found in feed {rss_feed['url']}")

            # 5. Insert all collected feeds
            if all_items:
                self.mongo_manager.insert_list(all_items, RSS_COLLECTION)
                logger.info(f"Inserted {len(all_items)} total items into feeds collection")

            # 6. Update execution record as success
            end_time = datetime.now()
            execution_duration = (end_time - start_time).total_seconds()

            self.mongo_manager.update_one(
                {"_id": execution_id},
                {"$set": {"status": "success", "execution_duration": execution_duration}},
                "process_execution_logs",
            )
            logger.info(f"Successfully completed RSS collection in {execution_duration:.2f} seconds")

        except Exception as e:
            # 7. Update execution record as failed on error
            end_time = datetime.now()
            execution_duration = (end_time - start_time).total_seconds()

            self.mongo_manager.update_one(
                {"_id": execution_id},
                {
                    "$set": {
                        "status": "failed",
                        "error_message": str(e),
                        "execution_duration": execution_duration,
                    }
                },
                "process_execution_logs",
            )
            logger.error(f"RSS collection failed after {execution_duration:.2f} seconds: {str(e)}")
            raise
