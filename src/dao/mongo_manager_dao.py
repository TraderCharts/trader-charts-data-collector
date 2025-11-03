import logging

from pymongo import MongoClient

logger = logging.getLogger(__name__)


class MongoManagerDAO:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def insert_dataframe(self, df, collection_name: str):
        """Insert a DataFrame into specified MongoDB collection"""
        collection = self.db[collection_name]
        records = df.to_dict(orient="records")
        print(f"🔍 Ready to insert {len(records)} records into MongoDB collection '{collection_name}'")
        if records:
            result = collection.insert_many(records)
            print(f"✅ Inserted {len(result.inserted_ids)} records into MongoDB.")
        else:
            print("⚠️ No records to insert.")

    def insert_list(self, records: list[dict], collection_name: str):
        """
        Insert a list of dictionaries into MongoDB collection.
        Avoids duplicates based on the 'link' field.
        """
        collection = self.db[collection_name]
        logger.info(f"Ready to insert {len(records)} records into MongoDB collection '{collection_name}'")

        if records:
            # Avoid duplicates by 'link'
            new_records = [r for r in records if not collection.find_one({"link": r.get("link")})]

            if new_records:
                result = collection.insert_many(new_records)
                logger.info(f"Inserted {len(result.inserted_ids)} new records into MongoDB.")
            else:
                logger.warning("All records already exist.")
        else:
            logger.warning("No records to insert.")

    def insert_one(self, document: dict, collection_name: str):
        """
        Insert a single document into specified MongoDB collection.
        Returns the inserted document's _id.
        """
        collection = self.db[collection_name]
        if not document.get("_id"):
            from bson import ObjectId

            document["_id"] = ObjectId()

        result = collection.insert_one(document)
        logger.info(f"Inserted single document with _id: {result.inserted_id} into collection '{collection_name}'")
        return result.inserted_id

    def find_one(self, query: dict, collection_name: str) -> dict | None:
        """Find one document in specified collection"""
        collection = self.db[collection_name]
        return collection.find_one(query)

    def find(self, query: dict, collection_name: str, sort: list | None = None):
        """Find documents in specified collection"""
        collection = self.db[collection_name]
        cursor = collection.find(query)
        if sort:
            cursor = cursor.sort(sort)
        return list(cursor)

    def delete_many(self, query: dict, collection_name: str):
        """Delete multiple documents from specified collection"""
        collection = self.db[collection_name]
        result = collection.delete_many(query)
        logger.info(f"Deleted {result.deleted_count} documents from collection '{collection_name}'")
        return result.deleted_count

    def update_one(self, query: dict, update: dict, collection_name: str):
        """Update one document in specified collection"""
        collection = self.db[collection_name]
        result = collection.update_one(query, update)
        return result
