import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import datetime

from database import AgentDataBase


class EitaaAgent:

    def __init__(self):
        self.db = AgentDataBase()

    def crawl_and_insert_specific_date(self, url, start_date, end_date):
        message_number = 0
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        while True:
            message_number += 1
            url = f"{url}{message_number}"
            response = requests.get(url)
            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.content, "html.parser")

            message_title = None
            message_text = None
            message_time = None
            message_view = None
            message_date = None
            message_id = None
            name = None
            username = None

            # Extract message title
            author_element = soup.find("div", class_="etme_widget_message_author accent_color")
            if author_element:
                owner_name_element = author_element.find("a", class_="etme_widget_message_owner_name")
                if owner_name_element:
                    span_element = owner_name_element.find("span", dir="auto")
                    if span_element:
                        message_title = span_element.get_text(strip=True)
                        print(message_title)
            # Extract message text
            text_element = soup.find("div", class_="etme_widget_message_text js-message_text")
            if text_element:
                message_text = text_element.get_text()
                print(message_text)
            # Extract message view
            view_element = soup.find("span", class_="etme_widget_message_views")
            if view_element:
                message_view = view_element.get_text()
                print(message_view)
            # Extract message time
            time_element = soup.find("time", class_="time")
            if time_element:
                message_time = time_element.get_text()
                print(message_time)
            # Extract message date
            date_element = soup.find("time", class_="time")
            if date_element:
                message_date = date_element.get("datetime")
                print(message_date)
            # Extract message id
            id_element = soup.find("div", class_="etme_widget_message_wrap js-widget_message_wrap")
            if id_element:
                message_id = id_element.get("id")
                print(message_id)
            # Extract the group or channel name
            header_element = soup.find("div", class_="etme_channel_info_header_title")
            if header_element:
                span_element = header_element.find("span", dir="auto")
                if span_element:
                    name = span_element.get_text(strip=True)
                    print(name)
            # Extract the username
            header_element = soup.find("div", class_="etme_channel_info_header_username")
            if header_element:
                a_element = header_element.find("a", dir="auto")
                if a_element:
                    username = a_element.get_text()
                    print(username)

            message = {
                "id": message_id,
                "title": message_title,
                "text": message_text,
                "view": message_view,
                "time": message_time,
                "date": message_date,
                "name": name,
                "username": username
            }
            if message_date:
                message_date = datetime.strptime(message_date, "%Y-%m-%dT%H:%M:%S%z").date()
                if start_date <= message_date <= end_date:
                    self.db.upsert(message)


if __name__ == '__main__':
    x = EitaaAgent()
    messages = x.crawl_from_last("https://eitaa.com/akhbarefori", 100)
    print(f"Number of messages retrieved: {len(messages)}")