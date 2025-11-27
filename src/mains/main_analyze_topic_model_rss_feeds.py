import logging
import logging.config
from datetime import datetime

import yake

from config import MONGO_DB_NAME, MONGO_URI
from dao.mongo_manager_dao import MongoManagerDAO
from logging_config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class SimpleTopicAnalyzer:
    def __init__(self, mongo_manager_dao):
        self.mongo_manager = mongo_manager_dao
        logger.info("Loading YAKE keyword extractor for Spanish...")
        self.kw_extractor = yake.KeywordExtractor(
            lan="es",  # Spanish language
            n=2,  # Max 3 words per keyphrase
            dedupLim=0.2,  # Deduplication threshold
            top=6,  # Top 10 keyphrases
            windowsSize=5,  # Context window size
        )

    def _prepare_text(self, item):
        """Prepare text by combining title, summary and content"""
        title = item.get("title", "")
        description = item.get("description", "")
        summary = item.get("summary", "")
        content = item.get("content", "").strip()

        # Join with periods to separate sentences
        full_text = f"{title}. {description}. {content}. {summary}"
        return full_text[:2000]  # Limit length for processing

    def analyze_feed(self, feed):
        """Analyze a single feed and extract keyphrases using YAKE"""
        try:
            text = self._prepare_text(feed)

            if not text.strip() or len(text.strip()) < 20:
                logger.warning(f"Skipping feed with insufficient text: {feed.get('title', 'No title')}")
                return None

            logger.debug(f"Processing text: {text[:100]}...")

            # Extract keywords using YAKE
            keywords = self.kw_extractor.extract_keywords(text)

            # DEBUG: Log the raw keyphrases
            logger.debug(f"Raw keyphrases: {keywords}")

            # Prepare analysis document - note: YAKE returns (phrase, score) where LOWER score is better
            analysis_doc = {
                "feedId": feed["_id"],
                "analysis_date": datetime.now(),
                "keyphrases": [{"phrase": phrase, "score": float(score)} for phrase, score in keywords],
                "text_preview": text[:500] + "..." if len(text) > 500 else text,
                "source": feed.get("source", ""),
                "title": feed.get("title", ""),
                "processed_text_length": len(text),
            }

            return analysis_doc

        except Exception as e:
            logger.error(f"Error analyzing feed {feed.get('_id', '')}: {e}")
            return None

    def process_feeds(self, limit=None):
        """Process all RSS feeds and save topic analysis"""
        logger.info("Starting automatic topic analysis for RSS feeds with YAKE")

        # Get RSS feeds
        query = {}
        if limit:
            feeds = self.mongo_manager.find(query, "rss_feeds_data", limit=limit)
        else:
            feeds = self.mongo_manager.find(query, "rss_feeds_data")

        logger.info(f"Feeds to analyze: {len(feeds)}")

        processed_count = 0
        successful_count = 0
        results = []

        for feed in feeds:
            try:
                processed_count += 1

                # Analyze feed
                analysis = self.analyze_feed(feed)

                if analysis:
                    # Save to MongoDB
                    self.mongo_manager.insert_one(analysis, "feed_topic_analysis")
                    results.append(analysis)
                    successful_count += 1

                # Show progress every 10 feeds
                if processed_count % 10 == 0:
                    logger.info(f"Processed: {processed_count}/{len(feeds)}")

                # Log first few examples
                if successful_count <= 3 and analysis:
                    top_phrases = [kp["phrase"] for kp in analysis["keyphrases"][:3]]
                    logger.info(f"Sample analysis - Title: {feed.get('title', '')[:60]}...")
                    logger.info(f"  Top phrases: {top_phrases}")

            except Exception as e:
                logger.error(f"Error processing feed {feed.get('_id', '')}: {e}")
                continue

        # Show summary
        logger.info("Topic analysis completed successfully")
        logger.info(f"Analyzed: {successful_count}/{len(feeds)} feeds")

        # Show most common keyphrases across all feeds
        if results:
            all_phrases = {}
            for result in results:
                for kp in result["keyphrases"][:5]:  # Top 5 phrases per feed
                    phrase = kp["phrase"]
                    all_phrases[phrase] = all_phrases.get(phrase, 0) + 1

            logger.info("Most frequent keyphrases across all feeds:")
            for phrase, count in sorted(all_phrases.items(), key=lambda x: x[1], reverse=True)[:10]:
                logger.info(f"  {phrase}: {count} feeds")

        return results


def main():
    """Main function for automatic topic analysis"""
    logger.info("Starting YAKE-based topic analysis system")

    # MongoDB configuration
    mongo_manager = MongoManagerDAO(MONGO_URI, MONGO_DB_NAME)

    # Execute topic analysis
    analyzer = SimpleTopicAnalyzer(mongo_manager)
    analyzer.process_feeds(limit=None)  # Remove limit for full processing

    logger.info("Topic analysis completed. Results saved in: feed_topic_analysis")


if __name__ == "__main__":
    main()
