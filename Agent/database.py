from pymongo import MongoClient


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
