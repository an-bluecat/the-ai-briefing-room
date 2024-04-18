from newsplease import NewsPlease
from newsScraper import scrape_verge, scrape_cnbctech, scrape_techcrunch, scrape_and_group_by_source, format_grouped_titles_by_source, select_events_by_source
import datetime

'''
Attributes Json Example
{
  "authors": [],
  "date_download": null,
  "date_modify": null,
  "date_publish": "2017-07-17 17:03:00",
  "description": "Russia has called on Ukraine to stick to the Minsk peace process [news-please will extract the whole text but in this example file we needed to cut off here because of copyright laws].",
  "filename": "https%3A%2F%2Fwww.rt.com%2Fnews%2F203203-ukraine-russia-troops-border%2F.json",
  "image_url": "https://img.rt.com/files/news/31/9c/30/00/canada-russia-troops-buildup-.si.jpg",
  "language": "en",
  "localpath": null,
  "source_domain": "www.rt.com",
  "maintext": "Russia has called on Ukraine to stick to the Minsk peace process [news-please will extract the whole text but in this example file we needed to cut off here because of copyright laws].",
  "title": "Moscow to Kiev: Stick to Minsk ceasefire, stop making false \u2018invasion\u2019 claims",
  "title_page": null,
  "title_rss": null,
  "url": "https://www.rt.com/news/203203-ukraine-russia-troops-border/"
}
'''
today = datetime.date.today()

all_news = scrape_verge(
    today) + scrape_cnbctech(today) + scrape_techcrunch(today)

titles = [x[0] for x in all_news]
news_to_URL = {news[0].lower(): news[1] for news in all_news}

arr = ['alphabet x’s bellwether harnesses ai to help predict natural disasters', 'boston dynamics’ new atlas robot is a swiveling, shape-shifting nightmare', 'airchat, the buzzy new social app, could be great — or, it could succumb to the same fate as clubhouse', '7 waymo robotaxis block traffic to san francisco freeway on-ramp', 'nasa has greenlit plans to send a giant drone to saturn’s largest moon']


#print(news_to_URL)
url_arr = []
for title in arr:
    url_arr.append(news_to_URL[title.lower()])

article = NewsPlease.from_url(
   url_arr[2])
print(article)
print(article.title)
print(article.authors)
print(article.date_publish)
print(article.maintext)