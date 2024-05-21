from newsScraper import scrape_cnbctech, is_today
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

current_dat = datetime.now().date()

def test_scrape_cnbctech():
    url = 'https://techcrunch.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    data_links = soup.find_all('a', attrs={'data-destinationlink': True})
    
    # Debugging: print the number of data_links found
    print(f"Number of data links found: {len(data_links)}")
    
    # Extract the href attributes and text of these links
    articles = [[link.text.strip(), link['href']] for link in data_links if is_today(link['href'], current_dat) and len(link.text.strip()) > 0]
    print(articles)
    return articles

   
   
test_scrape_cnbctech()