from datetime import datetime, timedelta
import requests
from lxml import html
from database import AgentDataBase
from bs4 import BeautifulSoup


class EitaaAgent:

    def __init__(self):
        self.db = AgentDataBase()
        self.time_offset = timedelta(hours=3, minutes=30)  # use to adjust the time

    def crawl_insert_specific_date(self, url, start_date, end_date):
        message_number = 0
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        while True:
            message_number += 1
            message_url = f"{url}/{message_number}"
            response = requests.get(message_url)

            if response.status_code == 404:
                print("Not Found!")
                message_number -= 1
                continue

            if response.status_code != 200:
                print("Can not access the web")
                message_number -= 1
                break

            # Extract html content
            tree = html.fromstring(response.content)

            # Extracting specific message based on message_number
            message_xpath = f'//*[@id="{message_number}"]'
            message_element = tree.xpath(message_xpath)

            # if we don't have content go to the next message
            if not message_element:
                continue

            # control date for when over
            message_date = message_element[0].xpath('.//time[@class="time"]/@datetime')
            if datetime.strptime(message_date[0], "%Y-%m-%dT%H:%M:%S%z").date() < start_date:
                print("The date is less")
                continue
            if datetime.strptime(message_date[0], "%Y-%m-%dT%H:%M:%S%z").date() > end_date:
                print("The date is over")
                return

            # Extract the message_title
            message_title = message_element[0].xpath(
                './/div[@class="etme_widget_message_author accent_color"]'
                '//a[@class="etme_widget_message_owner_name"]//span[@dir="auto"]/text()')

            # Extract the message_text
            message_text = message_element[0].xpath('.//div[@class="etme_widget_message_text js-message_text"]/text()')

            # Extract the message_view
            message_view = message_element[0].xpath('.//span[@class="etme_widget_message_views"]/text()')

            # Extract the message_time
            displayed_time_elements = message_element[0].xpath('.//time[@class="time"]/text()')
            displayed_time = displayed_time_elements[0] if displayed_time_elements else None
            # Convert displayed time to a datetime object
            displayed_time_obj = datetime.strptime(displayed_time, "%H:%M").time()
            # Adjust datetime to match the displayed time (subtract offset)
            message_date_obj = datetime.strptime(message_date[0], "%Y-%m-%dT%H:%M:%S%z") if message_date else None
            adjusted_time_obj = (
                        datetime.combine(message_date_obj.date(), displayed_time_obj) + self.time_offset).time()
            adjusted_time = adjusted_time_obj.strftime("%H:%M")
            message_time = adjusted_time

            # Extract the message_id
            message_id = message_element[0].xpath('.//@id')

            # Extract the name of group/channel
            name = message_element[0].xpath('/html/body/header/div/div[3]/section/div/div[1]/div[1]/div[1]/span/text()')

            # Extract the username of the group/channel
            username = message_element[0].xpath('/html/body/header/div/div[3]/section/div/div[1]/div[2]/a/text()')

            message = {
                "id": message_id[0] if message_id else None,
                "title": message_title[0] if message_title else None,
                "text": message_text[0] if message_text else None,
                "view": message_view[0] if message_view else None,
                "time": message_time,
                "date": message_date[0] if message_date else None,
                "name": name[0] if name else None,
                "username": username[0] if username else None
            }

            # checking date
            if message["date"]:
                message_date_obj = datetime.strptime(message["date"], "%Y-%m-%dT%H:%M:%S%z").date()
                if start_date <= message_date_obj <= end_date:
                    self.db.upsert(message)

    def crawl_from_last(self, url, count):
        response = requests.get(url)

        if response.status_code == 404:
            print("Not Found! Maybe the internet is unstable")
            self.crawl_from_last(url, count)

        if response.status_code != 200:
            print("The connection has a problem!")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        messages = soup.find_all('div', class_="etme_widget_message_wrap js-widget_message_wrap")
        number = 0
        message_id = messages[-1].get('id')
        while number != count:
            response = requests.get(f"{url}/{message_id}")

            if response.status_code == 404:
                print("Not Found! Maybe the internet is unstable")
                continue

            if response.status_code != 200:
                print("Can not access the web")
                return

            print(f"ID: {message_id}")

            soup = BeautifulSoup(response.content, 'html.parser')

            # message with special Id
            message_element = soup.find('div', id=f"{message_id}")

            if message_element is None:
                message_id = str(int(message_id) - 1)
                continue

            # Extract the title of message
            message_author_element = message_element.find('div', class_="etme_widget_message_author accent_color")
            message_owner_name = message_author_element.find('a', class_="etme_widget_message_owner_name")
            message_title = message_owner_name.find('span', dir="auto").get_text()
            print(f"Title: {message_title}")

            # Extract the text of message
            message_text = message_element.find('div', class_="etme_widget_message_text js-message_text").get_text()
            print(f"Text: {message_text}")

            # Extract the view of message
            message_info = message_element.find('div', class_="etme_widget_message_info short js-message_info")
            message_view = message_info.find('span', class_="etme_widget_message_views").get_text()
            print(f"View: {message_view}")

            # Extract the time of message and the date of messsage
            message_meta_time = message_info.find('span', class_="etme_widget_message_meta")
            message_date_element = message_meta_time.find('a', class_="etme_widget_message_date")
            message_time_element = message_date_element.find('time')
            message_time = message_time_element.get_text()
            message_date = message_time_element['datetime']
            displayed_time_obj = datetime.strptime(message_time, "%H:%M").time()
            message_date_obj = datetime.strptime(message_date, "%Y-%m-%dT%H:%M:%S%z").date()
            adjusted_time_obj = (datetime.combine(message_date_obj, displayed_time_obj) + self.time_offset).time()
            message_time = adjusted_time_obj.strftime("%H:%M")

            print(f"Time: {message_time}")
            print(f"Date: {message_date}")

            # Extract the name of group or channel
            message_header_title = soup.find('div', class_="etme_channel_info_header_title")
            message_name = message_header_title.find('span', dir="auto").get_text()
            print(f"Name: {message_name}")

            # Extract the username of group or channel
            message_header_username = soup.find('div', class_="etme_channel_info_header_username")
            message_username_tag = message_header_username.find('a', dir="auto")
            message_username = message_username_tag['href']
            print(f"Username: {message_username}")

            message = {
                "id": message_id,
                "title": message_title,
                "text": message_text,
                "view": message_view,
                "time": message_time,
                "date": message_date,
                "name": message_name,
                "username": message_username
            }

            self.db.upsert(message)

            message_id = str(int(message_id) - 1)
            number += 1


if __name__ == '__main__':
    agent = EitaaAgent()
    # agent.crawl_insert_specific_date("https://eitaa.com/akhbarefori", "2024-08-04", "2024-08-04")
    agent.crawl_from_last("https://eitaa.com/akhbarefori", 100)
