from pymongo import MongoClient
from pymongo.errors import PyMongoError


class AgentDataBase:
    def __init__(self, client='mongodb://localhost:27017/', db_name='EitaaAgent', collection_name='message'):
        self.client = MongoClient(client)
        self.database = self.client[db_name]
        self.collection = self.database[collection_name]

    def upsert(self, message_dict):
        existing_doc = self.collection.find_one({'Message_id': message_dict['Message_id']})
        if existing_doc:
            self.collection.replace_one({'Message_id': existing_doc['Message_id']}, message_dict)
        else:
            self.collection.insert_one(message_dict)

        print("The message was upserted")

    def close(self):
        if self.client:
            self.client.close()
            self.client = None

    def clear_database(self):
        self.collection.delete_many()

    def check_connection(self):
        try:
            server_status = self.database.command("serverStatus")
            return {"Status": "success", "Message": "Database connected successfully", "Server_host": server_status["host"]}
        except PyMongoError as e:
            return {"status": "error", "messasge": f"Database connection failed: {e}"}
        except Exception as e:
            return {"status": "error", "message":f"Database error: {e}"}