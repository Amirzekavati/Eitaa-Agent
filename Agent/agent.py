from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from database import AgentDataBase

class EitaaAgent:
    def __int__(self):
        self.db = AgentDataBase()
        self.message_number = 0

    def crawl_and_insert_specific_date(self, url, start_date, end_date):

        start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S%z").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S%z").date() + timedelta(
            days=1)  # Inclusive of end date

        while True:
            self.message_number += 1
            url = f"{url}{self.message_number}"
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
            # Extract the group or channel name
            name = soup.find("div", class_="etme_channel_info_header_title").find("span", dir="auto").get_text(strip=True)
            # Extract the username
            username = soup.find("div", class_="etme_channel_info_header_username").find("a", dir="auto").get_text()

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

            message_date = datetime.strptime(message_date, "%Y-%m-%dT%H:%M:%S%z").date()
            if start_date <= message_date <= end_date:
                self.db.upsert(message)
