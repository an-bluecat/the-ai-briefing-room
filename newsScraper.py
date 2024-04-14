
import requests
from bs4 import BeautifulSoup
import datetime
import re
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os


def is_today(date_input, current_date):
    if isinstance(date_input, datetime.datetime):
        return date_input.date() == current_date
    elif isinstance(date_input, str):
        try:
            match = re.search(r'(\d{4}/\d{1,2}/\d{1,2})', date_input)
            if match:
                date_part = match.group(1)
                parsed_date = datetime.datetime.strptime(date_part, "%Y/%m/%d").date()
                return parsed_date == current_date
        except ValueError as e:
            print(f"Error parsing date: {e}")
    return False        

def scrape_verge(current_date):
    url = 'https://www.theverge.com/tech'
    base_url = 'https://www.theverge.com'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.find_all('a', {'class': 'group hover:text-white'})

    articles = [[item.get('aria-label'), base_url + item['href']] for item in items if is_today(item['href'], current_date)]
    return articles

def scrape_cnbctech(current_date):
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
            # convert Sat, Apr 13th 2024 to 2024-04-13
            date_str = re.sub(r'(st|nd|rd|th)', '', publication_time)    
            date_object = datetime.datetime.strptime(date_str, '%a, %b %d %Y')
            if is_today(date_object, current_date):
                articles.append([title, link])
                
    return articles

def scrape_techcrunch(current_date):
    url = 'https://techcrunch.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.find_all('h2', class_='post-block__title') + soup.find_all('h3', class_='mini-view__item__title')
    articles = [[item.text.strip(), item.a['href']] for item in items if is_today(item.a['href'], current_date)]    
    return articles

def classify_titles(titles):
    prompt_text = "Being accurate and specific as possible, group the following news titles by the event they discuss:\n\n" + "\n".join(f"{i+1}. {title}" for i, title in enumerate(titles))
   # print((prompt_text))
    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
                messages=[
                {"role": "system", "content": "You are classifying news titles together into specific events. Output the response as a dictionary of specific event names and the titles that belong to them."},
                {"role": "user", "content": prompt_text}
                ]
        )
        print(response)
        output = response.choices[0].message.content
        return output
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



if __name__ == '__main__':
    load_dotenv()
    TEXT_MODEL = "gpt-4-turbo-preview"
    client = OpenAI()
    client.api_key = os.getenv('OPENAI_API_KEY')


    #today = datetime.date.today()
    today = datetime.date(2024, 4, 12)
   # print(today)

    all_news = scrape_verge(today) + scrape_cnbctech(today) + scrape_techcrunch(today)
    titles = [news[0] for news in all_news]
        
    grouped_titles = classify_titles(titles)
    if grouped_titles:
        print(grouped_titles)
    else:
        print("Failed to group the titles.")
    
    


        
        

