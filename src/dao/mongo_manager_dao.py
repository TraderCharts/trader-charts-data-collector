from pymongo import MongoClient

class MongoManagerDAO:
    def __init__(self, uri: str, db_name: str, collection_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_dataframe(self, df):
        records = df.to_dict(orient="records")
        print(f"🔍 Ready to insert {len(records)} records into MongoDB")
        if records:
            result = self.collection.insert_many(records)
            print(f"✅ Inserted {len(result.inserted_ids)} records into MongoDB.")
        else:
            print("⚠️ No records to insert.")
