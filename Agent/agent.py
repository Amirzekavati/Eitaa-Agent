from datetime import datetime, timedelta
import requests
from lxml import html
from database import AgentDataBase
from bs4 import BeautifulSoup

class EitaaAgent:

    def __init__(self):
        self.db = AgentDataBase()

    def crawl_insert_specific_date(self, url, start_date, end_date):
        message_number = 0
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        time_offset = timedelta(hours=3, minutes=30)  # use to adjust the time

        while True:
            message_number += 1
            message_url = f"{url}/{message_number}"
            response = requests.get(message_url)

            if response.status_code == 404:
                print("Not Found!")
                message_number -= 1
                continue
            if response.status_code != 200:
                print("Cannot access the web")
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
            if datetime.strptime(message_date[0], "%Y-%m-%dT%H:%M:%S%z").date() > end_date:
                print("The date is over")
                break

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
            adjusted_time_obj = (datetime.combine(message_date_obj.date(), displayed_time_obj) + time_offset).time()
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

    def crawl_from_last(self,url, count):
        response = requests.get(url)
        while response.status_code != 200:
            response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        messages = soup.find_all('div', class_="etme_widget_message_wrap js-widget_message_wrap")
        number = 0
        message_id = messages[-1].get('id')
        print(message_id)
        # while number != count:
        #     response = requests.get(f"{url}/{message_id}")
        #     soup = BeautifulSoup(response.content, 'html.parser')
        #     message_element = soup.find('div', id=f"{message_id}")
        #     message_author_element = message_element.find('div', class_="etme_widget_message_author accent_color")
        #     message_owner_name = message_author_element.find('a', class_="etme_widget_message_owner_name")
        #     message_text = message_owner_name.find('span', dir="auto").get_text(strip=True)
        #     print(message_text)
        #     break
            # message = {
            #     "id": message_id,
            #     "title":
            #     "text": message_text[0] if message_element else None,
            #     "view": message_view[0] if message_element else None,
            #     "time": message_time,
            #     "date": message_date[0] if message_element else None,
            #     "name": name[0] if name else None,
            #     "username": username[0] if username else None
            # }
        

if __name__ == '__main__':
    agent = EitaaAgent()
    # agent.crawl_insert_specific_date("https://eitaa.com/akhbarefori", "2024-08-04", "2024-08-04")
    agent.crawl_from_last("https://eitaa.com/akhbarefori", 100)
