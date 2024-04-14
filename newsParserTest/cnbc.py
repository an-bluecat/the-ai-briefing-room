from bs4 import BeautifulSoup
import requests
import datetime
import re

url = 'https://www.cnbc.com/technology/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
article_cards = soup.find_all('div', class_='Card-standardBreakerCard')
articles = []

for card in article_cards:
    title_tag = card.find('a', class_='Card-title')
    time_tag = card.find('span', class_='Card-time')
    if title_tag and time_tag:
        title = title_tag.text.strip()
        link = title_tag['href']
        publication_time = time_tag.text.strip()
        current_date = datetime.date(2024, 4, 11)
        # check if the article is from today
        match = re.search(r'(\d{4}/\d{1,2}/\d{1,2})', link)
        if match:
            date_part = match.group(1)
            news_date = datetime.datetime.strptime(date_part, "%Y/%m/%d").date()
            if news_date == current_date:

        
                articles.append((title, link, publication_time))


print(articles)
