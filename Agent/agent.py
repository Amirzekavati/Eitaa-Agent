import requests
from bs4 import BeautifulSoup

base_url = "https://eitta.com/s/akhbarefori/"
message_number = 1
messages = []

while True:
    url = f"{base_url}{message_number}"
    response = requests.get(url)
    if response.status_code != 200 :
        break

    soup = BeautifulSoup(response.content, "html.parser")

