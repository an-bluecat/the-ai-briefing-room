from bs4 import BeautifulSoup
import requests
import datetime
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time


url = "https://www.theinformation.com/technology?view=recent"


webdriver_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=webdriver_service)

driver.get(url)

time.sleep(3)

try:
    # Navigate to the URL
    driver.get(url)
    time.sleep(3)  # Allow some time for the page to load

    # Find all news items; adjust the selector as needed based on the actual page structure
    news_elements = driver.find_elements(By.CSS_SELECTOR, 'h3 a')  # Example CSS selector

    # Collecting news data
    news_data = []
    for element in news_elements:
        title = element.text.strip()  # Text of the element
        link = element.get_attribute('href')  # URL in the href attribute
        news_data.append({'title': title, 'link': link})

    # Print or process news data
    for news in news_data:
        print(f"Title: {news['title']}, URL: {news['link']}")

finally:
    # Close the browser session
    driver.quit()
