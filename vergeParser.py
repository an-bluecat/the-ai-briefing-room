from bs4 import BeautifulSoup
import requests
import datetime
import re


url = 'https://www.theverge.com/tech'
base_url = 'https://www.theverge.com'
#current_date = datetime.date.today()
current_date = datetime.date(2024, 4, 11)

def is_today(url):
    # Extract the date part from the URL
    match = re.search(r'(\d{4}/\d{1,2}/\d{1,2})', url)
    

    if match:
        date_part = match.group(1)
        news_date = datetime.datetime.strptime(date_part, "%Y/%m/%d").date()
        return news_date == current_date
    return False



response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

items = soup.find_all('a', {'class': 'group hover:text-white'})

parsed_items = [[item.get('aria-label'), base_url+item['href']] for item in items if is_today(item['href'])]

for i in parsed_items:
    print(i)

