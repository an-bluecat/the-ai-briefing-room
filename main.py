import logging
import time
import openai
from pathlib import Path
import os
from dotenv import load_dotenv
import datetime
from newsScraper import scrape_verge, scrape_cnbctech, scrape_techcrunch


# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration constants
TEXT_MODEL = "gpt-4-turbo-preview"
MAX_RETRIES = 1
RETRY_DELAY = 2  # seconds in case of retries
OUTPUT_DIRECTORY = './output/'  # Default output directory for files

class NewsPodcastOrchestrator:
    """ Orchestrates the creation of a podcast script from scraped news, using OpenAI's GPT models. """

    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

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

    def get_top_news(self, titles):
        """ Determines the top news titles from a list of scraped titles. """
        input_ask = "Identify the top 3 most popular or important news stories from the following news titles of today:\n\n" + \
            "\n".join(titles)
        return self.ask_gpt(input_ask).split('\n') if self.ask_gpt(input_ask) else []

    def generate_podcast_script(self, top_news):
        """ Generates a podcast script based on the top news titles. """
        news_concat = " ".join(top_news)
        input_ask = f"Create a podcast script under 200 words using these top news stories with a tone similar to CNBC TechCheck Briefings: {news_concat}"
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


# Example usage:
if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    api_key = os.getenv('OPENAI_API_KEY')
    # titles = ['X is removing ability to hide checkmarks for premium users', 'OpenAI makes ChatGPT ‘more direct, less verbose’', 'Virtual physical therapist Hinge Health lays off 10% of its workforce', 'Space Force tees up new ‘responsive space’ mission from Rocket Lab and True Anomaly', 'Ford’s hands-free BlueCruise system was active before fatal Texas crash', 'Internal pre-Starlink SpaceX financials show big spending on moonshot bets', 'Walmart will deploy robotic forklifts in its distribution centers', 'US says Russian hackers stole federal government emails during Microsoft cyberattack', 'Introducing the ScaleUp Startups Program at Disrupt 2024 for Series A to B startups', 'Taylor Swift’s music is back on TikTok, despite platform’s ongoing UMG dispute', 'Quibi redux? Short drama apps saw record revenue in Q1 2024', 'Megan Thee Stallion’s favorite app is Pinterest, obviously',
    #           'UK’s antitrust enforcer sounds the alarm over Big Tech’s grip on GenAI', 'Airtree Ventures already returned its first fund thanks to Canva while maintaining the majority of its stake', 'TechCrunch Minute: TikTok and Meta’s latest moves signal a more commodified internet', 'Cendana, Kline Hill have a fresh $105M to buy stakes in seed VC funds from LPs looking to sell', 'Lyrak to take on X by combining the best of Twitter with fediverse integration', 'Flipboard deepens its ties to the open source social web (aka the fediverse)', 'Substack now allows podcasters to sync and distribute their episodes to Spotify', 'Humane’s $699 Ai Pin is now available', 'Ford’s hands-free BlueCruise system was active before fatal Texas crash', 'Virtual physical therapist Hinge Health lays off 10% of its workforce', 'Humane’s Ai Pin considers life beyond the smartphone', 'US says Russian hackers stole federal government emails during Microsoft cyberattack']
    today = datetime.date(2024, 4, 12)

    all_news = scrape_verge(
        today) + scrape_cnbctech(today) + scrape_techcrunch(today)

    titles = [x[0] for x in all_news]
    output_directory = './output/'

    orchestrator = NewsPodcastOrchestrator(api_key)

    top_news = orchestrator.get_top_news(titles)
    if top_news:
        script = orchestrator.generate_podcast_script(top_news)
        if script:
            audio_file_path = orchestrator.text_to_speech(
                script, output_directory)
            if audio_file_path:
                logging.info(
                    f"Podcast production completed successfully. Audio file at: {audio_file_path}")

                output_file_path = f"{OUTPUT_DIRECTORY}podcast_data_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                with open(output_file_path, 'w') as file:
                    file.write("Titles:\n" + "\n".join(titles) + "\n\nTop News:\n" +
                               "\n".join(top_news) + "\n\nScript:\n" + script)
                    logging.info(f"All data saved to {output_file_path}.")

            else:
                logging.error("Failed to generate audio file.")
        else:
            logging.error("Failed to generate podcast script.")
    else:
        logging.error("Failed to identify top news.")
