import logging
import time
import openai
from pathlib import Path
import os
from dotenv import load_dotenv
import datetime
from newsScraper import scrape_verge, scrape_cnbctech, scrape_techcrunch, scrape_and_group_by_source, format_grouped_titles_by_source, select_events_by_source
from newsplease import NewsPlease
import re

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration constants
TEXT_MODEL = "gpt-4-turbo-preview"
MAX_RETRIES = 1
RETRY_DELAY = 2  # seconds in case of retries
OUTPUT_DIRECTORY = './output/'  # Default output directory for files
PRODUCTION_MODE = True  # Set to True to enable audio file generation


class NewsPodcastOrchestrator:
    """ Orchestrates the creation of a podcast script from scraped news, using OpenAI's GPT models. """

    def __init__(self, api_key, date, news_to_URL):
        self.client = openai.OpenAI(api_key=api_key)
        self.date = date
        self.news_to_URL = news_to_URL

    def ask_gpt(self, input_ask, role="system"):
        """ Sends a request to GPT model and handles retries if necessary. """
        attempts = 0
        while attempts < MAX_RETRIES:
            try:
                completion = self.client.chat.completions.create(
                    model=TEXT_MODEL,
                    messages=[{"role": "system", "content": role},
                              {"role": "user", "content": input_ask}]
                )
                response = completion.choices[0].message.content
                if isinstance(response, str):
                    return response.lower().strip().strip('.')
            except Exception as e:
                logging.error(f"Error in ask_gpt: {e}. Retrying...")
                time.sleep(RETRY_DELAY)
                attempts += 1
        return None
    

    def get_top_news(self):
        # get top news titles from the sources
        grouped_sources = scrape_and_group_by_source(self.date)
        formatted_text = format_grouped_titles_by_source(grouped_sources)
        input_ask = "You are creating newsletters for audience. From the list of sources and their news, consider the frequency of the event being discussed and how interesting audience find them to be. Then, select the top 5 news events that you would include in the newsletter:\n\n" + \
            "Grouped By Source:\n" + formatted_text
        role = "Output the response as string titles in the seperated by newline that are most important." 

        output = self.ask_gpt(input_ask, role)        
        return output.split('\n') if output else []

    def generate_podcast_script(self, top_news):
        """ Generates a podcast script based on the top news titles. """
        
        news_concat = []
        for news in top_news:
            if news not in self.news_to_URL:
                logging.warning(
                    f"News '{news}' not found in the available news sources.")
                return None
            
            curr_news = NewsPlease.from_url(self.news_to_URL[news])
            news_concat.append(curr_news.title + "\n" +curr_news.maintext)
            
        
        
        news_concat = "\n\n".join(news_concat)
        
        input_ask = f'''Create a podcast script under 500 words using these top news titles and content with a tone similar to CNBC TechCheck Briefings.
        Start with a sentence of introduction, and dive straight into news. Be sure to keep an interesting tone and pause/transition in between news. Also think about how to keep audience engaged.: {news_concat}
        '''
        return self.ask_gpt(input_ask)

    def text_to_speech(self, script, output_path):
        """ Converts the generated script to speech and saves the audio file. """
        try:
            response = self.client.audio.speech.create(
                model="tts-1", voice="alloy", input=script)
            speech_file_path = Path(
                output_path) / f"speech_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
            response.stream_to_file(speech_file_path)
            logging.info(f"Generated speech saved to {speech_file_path}.")
            return speech_file_path
        except Exception as e:
            logging.error(f"Failed to convert text to speech: {e}")
            return None

    def generate_podcast_title(self, transcript):
        """ Generates a podcast title from the provided transcript. """
        input_ask = "Generate a title for this podcast. Include no more than three key topics (if there are many, choose the three most important ones). Incorporate emojis where appropriate. Follow the style of titles such as: 'Tesla Showcases FSD Demo 🚗, Adam Neuman's WeWork Bid 💰, CSV Conundrums 🖥️','Anthropic’s $4B Amazon Boost 💰, Brex's Valuation Leap to $12B 💳, Strategies for Success ✨','The OpenAI Voice Revolution 🗣️, AI Safety Measures 🦺, LLMs Go Mobile 📱'. Here's the transcript excerpt: " + transcript
        return self.ask_gpt(input_ask)


def remove_leading_numbers(lst):
    # This regular expression matches any leading numbers followed by a dot and any amount of whitespace
    pattern = re.compile(r'^\d+\.\s*')
    # This will apply the regex substitution to each string in the list
    return [pattern.sub('', s) for s in lst]

# Example usage:
if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    api_key = os.getenv('OPENAI_API_KEY')
    # titles = ['X is removing ability to hide checkmarks for premium users', 'OpenAI makes ChatGPT ‘more direct, less verbose’', 'Virtual physical therapist Hinge Health lays off 10% of its workforce', 'Space Force tees up new ‘responsive space’ mission from Rocket Lab and True Anomaly', 'Ford’s hands-free BlueCruise system was active before fatal Texas crash', 'Internal pre-Starlink SpaceX financials show big spending on moonshot bets', 'Walmart will deploy robotic forklifts in its distribution centers', 'US says Russian hackers stole federal government emails during Microsoft cyberattack', 'Introducing the ScaleUp Startups Program at Disrupt 2024 for Series A to B startups', 'Taylor Swift’s music is back on TikTok, despite platform’s ongoing UMG dispute', 'Quibi redux? Short drama apps saw record revenue in Q1 2024', 'Megan Thee Stallion’s favorite app is Pinterest, obviously',
    #           'UK’s antitrust enforcer sounds the alarm over Big Tech’s grip on GenAI', 'Airtree Ventures already returned its first fund thanks to Canva while maintaining the majority of its stake', 'TechCrunch Minute: TikTok and Meta’s latest moves signal a more commodified internet', 'Cendana, Kline Hill have a fresh $105M to buy stakes in seed VC funds from LPs looking to sell', 'Lyrak to take on X by combining the best of Twitter with fediverse integration', 'Flipboard deepens its ties to the open source social web (aka the fediverse)', 'Substack now allows podcasters to sync and distribute their episodes to Spotify', 'Humane’s $699 Ai Pin is now available', 'Ford’s hands-free BlueCruise system was active before fatal Texas crash', 'Virtual physical therapist Hinge Health lays off 10% of its workforce', 'Humane’s Ai Pin considers life beyond the smartphone', 'US says Russian hackers stole federal government emails during Microsoft cyberattack']
   # today = datetime.date(2024, 4, 12)
    today = datetime.date.today()

    all_news = scrape_verge(
        today) + scrape_cnbctech(today) + scrape_techcrunch(today)

    titles = [x[0] for x in all_news]
    news_to_URL = {news[0].lower(): news[1] for news in all_news}

    output_directory = './output/'

    orchestrator = NewsPodcastOrchestrator(api_key, today, news_to_URL)

    top_news = orchestrator.get_top_news()
    
    if top_news:
        script = orchestrator.generate_podcast_script(remove_leading_numbers(top_news))
        podcast_title = orchestrator.generate_podcast_title(script)
        if script and podcast_title:
            if PRODUCTION_MODE:
                audio_file_path = orchestrator.text_to_speech(
                    script, output_directory)
                if audio_file_path:
                    logging.info(
                        f"Podcast production completed successfully. Audio file at: {audio_file_path}")

                # Prepare the output text data
                output_data = f"Titles:\n{chr(10).join(titles)}\n\nTop News:\n{chr(10).join(top_news)}\n\nScript:\n{script}\n\nPodcast Title:\n{podcast_title}\n"
                output_file_path = f"{OUTPUT_DIRECTORY}podcast_data_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

                # Write the output data to the file
                with open(output_file_path, 'w') as file:
                    file.write(output_data)
                    logging.info(f"All data saved to {output_file_path}.")

            else:
                logging.error("Failed to generate audio file.")
        else:
            logging.error("Failed to generate podcast script or title.")
    else:
        logging.error("Failed to identify top news.")
    
