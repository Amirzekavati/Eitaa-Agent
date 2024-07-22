from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode for no UI
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration

# Path to your ChromeDriver
chrome_driver_path = 'C:\Program Files\chromedriver\chromedriver.exe'  # Update this path

# Set up the Chrome driver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the URL
url = "https://eitaa.com/s/akhbarefori/400"  # Replace with your URL
driver.get(url)

# Interact with the page or extract information
# For example, find elements or extract content
# Example: print page title
print(driver.title)

# Close the driver
driver.quit()

