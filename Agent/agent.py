import requests
from bs4 import BeautifulSoup

base_url = "https://eitaa.com/s/akhbarefori/"
message_number = 1
messages = []

while True:
    url = f"{base_url}{message_number}"
    response = requests.get(url)
    if response.status_code != 200 :
        break

    soup = BeautifulSoup(response.content, "html.parser")

    message_title = soup.find(class_="etme_widget_message_owner_name").find("span").get_text(strip=True)
    message_text = soup.find(class_="etme_widget_message_text js-message_text")
    message_view = soup.find(class_="etme_widget_message_info short js-message_info").find("span").get_text(strip=True)
    message_time = soup.find(class_="time")
    message_date = soup.find("a", class_="etme_widget_message_date").find("time").get("datetime")


    message = {
        "message_number": message_number,
        "message_title": message_title,
        "message_text": message_text,
        "message_view": message_view,
        "message_time": message_time,
        "message_date": message_date
    }
    messages.append(message)
    print(f"scraped message {message_number}")

    message_number += 1

    for message in messages:
        print(message)

