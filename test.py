from newsplease import NewsPlease
from newsScraper import scrape_verge, scrape_cnbctech, scrape_techcrunch, scrape_and_group_by_source, format_grouped_titles_by_source, select_events_by_source
import datetime
import os
import requests
from dotenv import load_dotenv
from utils import get_day_of_week, spanish_title_case, english_title_case

load_dotenv()

print(get_day_of_week(datetime.date.today().strftime('%Y-%m-%d')))  


