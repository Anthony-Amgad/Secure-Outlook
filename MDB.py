import certifi
from pymongo import MongoClient

class MDB:
    MONGO_URI = "REDACTED"
    DATABASE_NAME = 'KeyDB'
    COLLECTION_NAME = 'PublicKeys'

    def getKey(self, email):
        client = MongoClient(self.MONGO_URI, tlsCAFile=certifi.where())
        collection = client[self.DATABASE_NAME][self.COLLECTION_NAME]
        try:
            key = collection.find({"email":email})[0]
            client.close()
            return key["key"]
        except IndexError:
            client.close()
            return None

    def addKey(self, email, key):
        client = MongoClient(self.MONGO_URI, tlsCAFile=certifi.where())
        collection = client[self.DATABASE_NAME][self.COLLECTION_NAME]
        public_key_data = {
        "email":email,
        "key":key
        }
        result = collection.insert_one(public_key_data)
        client.close()

    def deleteKey(self, email):
        if self.getKey(email) != None:
            client = MongoClient(self.MONGO_URI, tlsCAFile=certifi.where())
            collection = client[self.DATABASE_NAME][self.COLLECTION_NAME]
            collection.delete_one({
            "email":email
            })
            client.close()

