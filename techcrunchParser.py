from bs4 import BeautifulSoup
import requests

url = 'https://techcrunch.com/'

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
items = soup.find_all('h2', class_='post-block__title') + \
    soup.find_all('h3', class_='mini-view__item__title')

parsed_items = [[item.text.strip(), item.a['href']] for item in items]

for item in parsed_items:
    print(item)
print([x[0] for x in parsed_items])
