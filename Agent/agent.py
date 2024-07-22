import requests
from bs4 import BeautifulSoup

base_url = "https://eitaa.com/s/akhbarefori/"
message_number = 1
messages = []

while True:
    url = f"{base_url}{message_number}"
    response = requests.get(url)
    if response.status_code != 200:
        break

    # Print the entire HTML content
    print(response.content)

    soup = BeautifulSoup(response.content, "html.parser")

    # Initialize variables to None
    message_title = None

    # Extract message title
    author_element = soup.find("div", class_="etme_widget_message_author accent_color")
    print("Author Element:", author_element)

    if author_element:
        owner_name_element = author_element.find("a", class_="etme_widget_message_owner_name")
        print("Owner Name Element:", owner_name_element)

        if owner_name_element:
            span_element = owner_name_element.find("span", dir="auto")
            print("Span Element:", span_element)

            if span_element:
                message_title = span_element.get_text(strip=True)

    print("Message Title:", message_title)
    break  # Added break to prevent an infinite loop during testing
