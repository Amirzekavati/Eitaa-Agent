import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

class EitaaAgent:

    def __init__(self, db_uri, db_name, collection_name):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def scrape_messages(self):
        message_number = 0

        while True:
            message_number += 1
            url = f"{self.base_url}{message_number}"
            response = requests.get(url)
            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.content, "html.parser")

            # Initialize variables to None
            message_title = None
            message_text = None
            message_view = None
            message_time = None
            message_date = None
            message_id = None

            # Extract message title
            author_element = soup.find("div", class_="etme_widget_message_author accent_color")
            if author_element:
                owner_name_element = author_element.find("a", class_="etme_widget_message_owner_name")
                if owner_name_element:
                    span_element = owner_name_element.find("span", dir="auto")
                    if span_element:
                        message_title = span_element.get_text(strip=True)

            # Extract message text
            message_text = soup.find("div", class_="etme_widget_message_text js-message_text").get_text()
            # Extract message view
            message_view = soup.find("span", class_="etme_widget_message_views").get_text()
            # Extract message time
            message_time = soup.find("time", class_="time").get_text()
            # Extract message date
            message_date = soup.find("time", class_="time").get("datetime")
            # Extract message id
            message_id = soup.find("div", class_="etme_widget_message_wrap js-widget_message_wrap").get("id")

            message_data = {
                "message_id": message_id,
                "message_title": message_title,
                "message_text": message_text,
                "message_view": message_view,
                "message_time": message_time,
                "message_date": message_date
            }

            # Insert message data into MongoDB
            self.collection.insert_one(message_data)

            print(f"The message with Id {message_id} was inserted to database")

# Example usage
if __name__ == "__main__":
    base_url = "https://eitaa.com/akhbarefori/"
    db_uri = 'mongodb://localhost:27017/'
    db_name = 'your_database_name'
    collection_name = 'messages'

    scraper = EitaaAgent(base_url, db_uri, db_name, collection_name)
    scraper.scrape_messages()
