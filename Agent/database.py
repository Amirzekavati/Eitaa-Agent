from pymongo import MongoClient
from pymongo.errors import PyMongoError


class AgentDataBase:
    def __init__(self, client='mongodb://localhost:27017/', db_name='EitaaAgent', collection_name='message'):
        self.client = MongoClient(client)
        self.database = self.client[db_name]
        self.collection = self.database[collection_name]

    def check_empty_collection(self, collection_name):
        collection = self.database[collection_name]
        count = collection.count_documents({})
        if count == 0:
            collection.insert_one({"id": 1})

    def upsert_link(self, link, collection_name='link'):
        collection = self.database[collection_name]
        existing_doc = collection.find_one({'link': link})
        if existing_doc:
            print("replace the link")
        else:
            collection.insert_one({'link': link})
            print("insert the link")

    def upsert(self, message_dict):
        existing_doc = self.collection.find_one({'id': message_dict['id']})
        if existing_doc:
            self.collection.replace_one({'id': existing_doc['id']}, message_dict)
            print("replace the messaged")
        else:
            self.collection.insert_one(message_dict)
            print("insert the message")

    def delete(self, message_dict):
        self.collection.delete_one(message_dict)
        print("The message was deleted successfully")

    def close(self):
        if self.client:
            self.client.close()
            self.client = None
        print("The database was closed")

    def clear_database(self):
        self.collection.delete_many({})
        print("clear the database")

    def check_connection(self):
        try:
            server_status = self.database.command("serverStatus")
            print("The connection is successful")
            return {"Status": "success", "Message": "Database connected successfully",
                    "Server_host": server_status["host"]}
        except PyMongoError as e:
            return {"status": "error", "Message": f"Database connection failed: {e}"}
        except Exception as e:
            return {"status": "error", "Message": f"Database error: {e}"}
