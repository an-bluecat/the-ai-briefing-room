from newsScraper import scrape_cnbctech, is_today, scrape_verge, scrape_techcrunch
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import datetime
from utils.utils import get_day_of_week, get_next_weekday, get_upload_date, spanish_title_case, english_title_case

today =   datetime.date.today()


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


print(get_upload_date('2024-05-21'))