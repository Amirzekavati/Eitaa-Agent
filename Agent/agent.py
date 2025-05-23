import requests
from bs4 import BeautifulSoup

base_url = "https://eitaa.com/akhbarefori/"
message_number = 0
messages = []

while True:
    message_number += 1
    url = f"{base_url}{message_number}"
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

    print("Message Id:", message_id)
    print("Message Title:", message_title)
    print("Message Text:", message_text)
    print("Message View:", message_view)
    print("Message Time:", message_time)
    print("Message Date:", message_date)

