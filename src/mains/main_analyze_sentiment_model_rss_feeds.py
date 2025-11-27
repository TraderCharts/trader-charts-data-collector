import logging.config
from datetime import datetime

from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

from config import MONGO_DB_NAME, MONGO_URI
from dao.mongo_manager_dao import MongoManagerDAO
from logging_config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class SentimentPredictor:
    def __init__(self, mongo_manager_dao):
        self.mongo_manager = mongo_manager_dao
        self.model, self.tokenizer, self.model_info = self._load_best_model()

        self.emoji_map = {"positive": "📈✅", "negative": "📉❌", "neutral": "➖⚪"}

    def _load_best_model(self):
        """Load the best fine-tuned BETO model"""
        # Si solo querés UN documento, usá find_one sin sort
        best_model = self.mongo_manager.find_one({"fine_tuned_from": "robertuito-base"}, "sentiment_model_metadata")

        if not best_model:
            raise ValueError("No fine-tuned BETO model found")

        # Si necesitás el más reciente, entonces SÍ necesitás find + sort + limit
        # Pero si con find_one te basta, dejalo así

        model_path = best_model["model_path"]
        logger.info(f"Loading best model: {best_model['model_name']}")

        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        return model, tokenizer, best_model

    def _prepare_text(self, item):
        """Prepare text by concatenating title, description and content"""
        title = item.get("title", "")
        description = item.get("description", "")
        summary = item.get("summary", "")
        content = item.get("content", "")

        # Join with periods to separate sentences
        full_text = f"{title}. {description}. {content}. {summary}"

        return full_text[:1000]  # Max 1000 characters

    def predict_sentiment(self, text):
        """Make prediction with all probabilities"""
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=self.model,
            tokenizer=self.tokenizer,
            return_all_scores=True,  # All probabilities
            device=0 if torch.backends.mps.is_built() else -1,
        )

        result = sentiment_pipeline(text[:512])[0]

        # Find prediction with highest probability
        best_pred = max(result, key=lambda x: x["score"])

        # Get all probabilities
        all_scores = {score["label"]: score["score"] for score in result}

        emoji = self.emoji_map.get(best_pred["label"], "➖⚪")

        return {
            "sentiment_label": best_pred["label"],
            "sentiment_confidence": best_pred["score"],
            "sentiment_emoji": emoji,
            "all_scores": all_scores,  # All scores
            "display_text": f"{emoji} {best_pred['label'].upper()} ({best_pred['score']:.1%})",
        }

    def process_rss_feeds(self, limit=None):
        """Process all RSS feeds and save predictions"""
        logger.info("Starting sentiment prediction for RSS feeds")

        # Get RSS feeds
        query = {}
        if limit:
            feeds = self.mongo_manager.find(query, "rss_feeds_data", limit=limit)
        else:
            feeds = self.mongo_manager.find(query, "rss_feeds_data")

        logger.info(f"Feeds to process: {len(feeds)}")

        processed_count = 0
        results = []

        for feed in feeds:
            try:
                # Prepare text
                text = self._prepare_text(feed)

                if not text.strip():
                    continue

                # Make prediction
                prediction = self.predict_sentiment(text)

                # Prepare document to save
                analysis_doc = {
                    "feedId": feed["_id"],
                    "model_used": self.model_info["model_id"],
                    "model_name": self.model_info["model_name"],
                    "sentiment_label": prediction["sentiment_label"],
                    "sentiment_confidence": prediction["sentiment_confidence"],
                    "sentiment_emoji": prediction["sentiment_emoji"],
                    "all_scores": prediction["all_scores"],  # All scores
                    "text_preview": text[:200] + "..." if len(text) > 200 else text,
                    "analysis_date": datetime.now(),
                    "source": feed.get("source", ""),
                    "pubDate": feed.get("pubDate", ""),
                }

                # Save to MongoDB
                self.mongo_manager.insert_one(analysis_doc, "feed_sentiment_analysis")

                results.append(analysis_doc)
                processed_count += 1

                # Show progress every 10 feeds
                if processed_count % 10 == 0:
                    logger.info(f"Processed: {processed_count}/{len(feeds)}")

                # Show some examples
                if processed_count <= 3:
                    logger.info(f"{prediction['sentiment_emoji']} '{feed.get('title', '')[:50]}...'")
                    logger.info(f"→ {prediction['display_text']}")
                    logger.info(f"Scores: {prediction['all_scores']}")

            except Exception as e:
                logger.error(f"Error processing feed {feed.get('_id', '')}: {e}")
                continue

        # Show final summary
        sentiment_counts = {}
        for result in results:
            label = result["sentiment_label"]
            sentiment_counts[label] = sentiment_counts.get(label, 0) + 1

        logger.info("Prediction completed")
        logger.info(f"Total processed: {processed_count}")
        logger.info("Sentiment distribution:")
        for label, count in sentiment_counts.items():
            percentage = (count / processed_count) * 100
            emoji = self.emoji_map.get(label, "➖⚪")
            logger.info(f"{emoji} {label}: {count} ({percentage:.1f}%)")

        return results


def main():
    """Main function for RSS feed sentiment prediction"""
    logger.info("Starting sentiment prediction system")

    # MongoDB configuration with generic DAO
    mongo_manager = MongoManagerDAO(MONGO_URI, MONGO_DB_NAME)

    # Import torch for device detection
    global torch
    import torch

    # Execute prediction
    predictor = SentimentPredictor(mongo_manager)
    predictor.process_rss_feeds(limit=None)

    logger.info("Results saved in: feed_sentiment_analysis")


if __name__ == "__main__":
    main()
