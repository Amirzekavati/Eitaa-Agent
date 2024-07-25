from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from database import AgentDataBase

class EitaaAgent:
    def __int__(self):
        self.db = AgentDataBase()

    def crawl_and_insert_into_database(self, url):
        message_number = 0

        while True:
            message_number += 1
            url = f"{url}{message_number}"
            response = requests.get(url)
            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract message title
            author_element = soup.find("div", class_="etme_widget_message_author accent_color")
            owner_name_element = author_element.find("a", class_="etme_widget_message_owner_name")
            span_element = owner_name_element.find("span", dir="auto")
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

            message = {
                "id": message_id,
                "title": message_title,
                "text": message_text,
                "view": message_view,
                "time": message_time,
                "date": message_date
            }

            self.db.upsert(message)

    def get_messages_between_dates(self, start_date, end_date):
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S%z").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S%z").date() + timedelta(
                days=1)  # Inclusive of end date

            query = {
                "date": {
                    "$gte": datetime.combine(start_date, datetime.min.time()),
                    "$lt": datetime.combine(end_date, datetime.min.time())
                }
            }

            messages = self.db.collection.find(query)
            return list(messages)
        except Exception as e:
            print(f"An error occurred while fetching messages: {e}")
            return []



# import requests
# from bs4 import BeautifulSoup
#
# base_url = "https://eitaa.com/akhbarefori/"
# message_number = 0
# messages = []
#
# while True:
#     message_number += 1
#     url = f"{base_url}{message_number}"
#     response = requests.get(url)
#     if response.status_code != 200:
#         break
#
#     soup = BeautifulSoup(response.content, "html.parser")
#
#     # Initialize variables to None
#     message_title = None
#     message_text = None
#     message_view = None
#     message_time = None
#     message_date = None
#     message_id = None
#
#     # Extract message title
#     author_element = soup.find("div", class_="etme_widget_message_author accent_color")
#     if author_element:
#         owner_name_element = author_element.find("a", class_="etme_widget_message_owner_name")
#         if owner_name_element:
#             span_element = owner_name_element.find("span", dir="auto")
#             if span_element:
#                 message_title = span_element.get_text(strip=True)
#
#     # Extract message text
#     message_text = soup.find("div", class_="etme_widget_message_text js-message_text").get_text()
#     # Extract message view
#     message_view = soup.find("span", class_="etme_widget_message_views").get_text()
#     # Extract message time
#     message_time = soup.find("time", class_="time").get_text()
#     # Extract message date
#     message_date = soup.find("time", class_="time").get("datetime")
#     # Extract message id
#     message_id = soup.find("div", class_="etme_widget_message_wrap js-widget_message_wrap").get("id")
#
#     message={
#         "id": message_id,
#         "title": message_title,
#         "text": message_text,
#         "view": message_view,
#         "time": message_time,
#         "date": message_date
#     }
#
#     print("Message Id:", message_id)
#     print("Message Title:", message_title)
#     print("Message Text:", message_text)
#     print("Message View:", message_view)
#     print("Message Time:", message_time)
#     print("Message Date:", message_date)
