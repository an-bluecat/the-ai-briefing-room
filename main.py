
from newsScraper import scrape_verge, scrape_cnbctech, scrape_techcrunch
import datetime


if __name__ == '__main__':
    
    #today = datetime.date.today()
    today = datetime.date(2024, 4, 12)
    print(today)
    #scrape_verge(today))
    #print(scrape_cnbctech(today))
    #print(scrape_techcrunch(today))
    
    
    all_news = scrape_verge(today) + scrape_cnbctech(today) + scrape_techcrunch(today)
    
    print(len(all_news))
    
    for news in all_news:
        print(news)
        
        