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
import difflib

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
        input_ask = "Suppose you are the chief editor at CNBC-TechCheck-Briefing. You need to select 5 most important news events to put into today's briefing(You might be able to see some hint by how many times a news event is reported, but also consider what your audience of CNBC-TechCheck-Briefing is interested in). Return the title of the event in order of importance for these unqiue events. \
            Here are the news of today:\n" + formatted_text
        role = "Output the response as string titles in the seperated by newline. Each title should be exactly how it is in the news source."

        output = self.ask_gpt(input_ask, role)
        return input_ask, output.split('\n') if output else []

    def generate_podcast_script(self, top_news):
        """ Generates a podcast script based on the top news titles. """

        news_concat = []
        for news in top_news:
            if news not in self.news_to_URL:
                # Search for news in the dictionary keys
                possible_news = difflib.get_close_matches(
                    news, self.news_to_URL.keys())

                # If a close match is found, use the full string as the key
                if possible_news:
                    news = possible_news[0]
                else:
                    logging.warning(
                        f"News '{news}' not found in the available news sources. Skipping")
                    continue
                logging.warning(
                    f"News '{news}' not found in the available news sources. Skipping")
                continue

            curr_news = NewsPlease.from_url(self.news_to_URL[news])
            news_concat.append(curr_news.title + "\n" + curr_news.maintext)

        news_concat = "\n\n".join(news_concat)
        first_shot = """
        Prompt: Give a quick tech news update script in the style of CNBC techcheck briefing as an example.
        Response: I'm Wall-E, and this is your CNBC techcheck Briefing. Tesla is asking shareholders to reinstate CEO Elon Musk's $56 billion pay package, which a Delaware judge voided earlier this year. The judge ruled that the record-setting compensation deal was, quote, deeply flawed. Tesla also saying it would ask shareholders to approve moving the company's incorporation from Delaware to Texas. The company has hired a proxy solicitor and plans to spend millions of dollars to help secure votes for the two proposals. Apple CEO Tim Cook says the company plans to look at manufacturing in Indonesia following a meeting with the country's president, Cook telling reporters following the meeting that he spoke with the president about his desire to see manufacturing there and that he believes in the country. The comments come as Apple is pushed to diversify its supply chain with more manufacturing outside of China in countries such as Vietnam and India. Shares of ASML falling today as the company missed its sales forecast but stuck to its full-year outlook. Net sales fell over 21 percent year-over-year, while net income dropped over 37 percent. ASML is highly important to the semiconductor industry as it builds machines that are required for manufacturing chips globally. Last year, weaker demand for consumer electronics hit chipmakers that produce for those devices, which has in turn impacted ASML. That's all for today. We'll see you back here tomorrow.
        """

        prompt = f"Prompt: Give a quick tech news update script in the style of CNBC techcheck briefing using the following news titles and content. Closely follow how CNBC techcheck chooses context to put into the script, the langauge style and sentence structure. Use the same beginning and ending(including host name), and replace CNBC techcheck briefing to 'AI briefing' \n {news_concat}\n"
        response_begin = "Response:"
        input_ask = first_shot + prompt + response_begin

        return input_ask, self.ask_gpt(input_ask)

    def polish_podcast_script(self, script):
        """Polishes the podcast script using the GPT API."""

        # Make a request to the GPT API to polish the script
        input_ask = script + """
        This is not up to standards with the style of 'CNBC techcheck', here is a example. Carefully inspect the language style, sentence structure, use of words and order of words in sentences of the following examples of 'CNBC techcheck':
example 1:
"I'm Julia Boorstin, and this is your tech Briefing. Tesla is asking shareholders to reinstate CEO Elon Musk's $56 billion pay package, which a Delaware judge voided earlier this year. The judge ruled that the record-setting compensation deal was, quote, deeply flawed. Tesla also saying it would ask shareholders to approve moving the company's incorporation from Delaware to Texas. The company has hired a proxy solicitor and plans to spend millions of dollars to help secure votes for the two proposals. Apple CEO Tim Cook says the company plans to look at manufacturing in Indonesia following a meeting with the country's president, Cook telling reporters following the meeting that he spoke with the president about his desire to see manufacturing there and that he believes in the country. The comments come as Apple is pushed to diversify its supply chain with more manufacturing outside of China in countries such as Vietnam and India. Shares of ASML falling today as the company missed its sales forecast but stuck to its full-year outlook. Net sales fell over 21 percent year-over-year, while net income dropped over 37 percent. ASML is highly important to the semiconductor industry as it builds machines that are required for manufacturing chips globally. Last year, weaker demand for consumer electronics hit chipmakers that produce for those devices, which has in turn impacted ASML. That's all for today. We'll see you back here tomorrow."
example 2: 
"I'm Steve Kovach, and this is your tech Briefing. AMD revealing today its latest AI chips. The new chips will be for so-called AI PCs, or PCs with special processors, for tasks like real-time language translation, or using tools like Microsoft's Copilot Assistant more efficiently. Last month, Intel put its latest AI PC chip in Microsoft's new Surface computer lineup, and Qualcomm is expected to put its chips in PCs starting next month. Sticking with AI, Microsoft announcing today a $1.5 billion investment in G42, a startup based in the United Arab Emirates. As part of the deal, G42 will use Microsoft's Azure Cloud to run its AI applications, and Microsoft President Brad Smith will join the company's board. Microsoft has made several foreign AI and cloud investments so far this year. Some examples include the company said it would open a headquarters in London, invest in the French startup Mistral, and invest $2.9 billion in AI infrastructure in Japan. Now over to China. Baidu, the Chinese search company, announced its AI chatbot ErnieBot has surpassed 200 million users. ErnieBot launched last year, and other companies like Samsung and Honor have integrated Ernie into their devices. Apple is reportedly going to partner with Baidu as well to help power new AI features in devices sold in China. That's all from today. We'll see you back here tomorrow."
Make my original podcast script more like the examples above to an extend that it is similar in style, language, sentence structure, and use of words and so closely resembled so that no one can tell the difference between the style.
refined podcast script:
"""
        role = "Output the polished script."
        polished_script = orchestrator.ask_gpt(input_ask, role)
        return polished_script

    def generate_podcast_description(self, script):
        """ Generates a podcast description from the provided script. """
        input_ask = """
            Generate a description for this podcast. Summarize the key topics discussed and highlight any interesting insights or takeaways. This will be the script we use for the podcast description on Apple Podcast. So please be concise, use bullet point when possible.
            Here's the podcast script: 
            {script}
            Description:
            """
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

    top_news_prompt, top_news = orchestrator.get_top_news()

    if top_news:
        generate_script_prompt, script = orchestrator.generate_podcast_script(
            remove_leading_numbers(top_news))

        polished_script = orchestrator.polish_podcast_script(script)
        podcast_description = orchestrator.generate_podcast_description(
            polished_script)
        podcast_title = orchestrator.generate_podcast_title(script)
        if polished_script and podcast_title:
            if PRODUCTION_MODE:
                audio_file_path = orchestrator.text_to_speech(
                    polished_script, output_directory)

                if audio_file_path:
                    logging.info(
                        f"Podcast production completed successfully. Audio file at: {audio_file_path}")
                else:
                    logging.error("Failed to generate audio file.")
            # Prepare the output text data
            output_data = f"Titles:\n{chr(10).join(titles)}\n\ntop_news_prompt: {top_news_prompt}\n\nTop News:\n{chr(10).join(top_news)}\n\nGenerate_scipt_prompt:\n{generate_script_prompt}\n\nScript:\n{script}\n\npolished_script:\n{polished_script}\n\nPodcast Title:\n{podcast_title}\n\npodcast_description:\n{podcast_description}\n"
            output_file_path = f"{OUTPUT_DIRECTORY}podcast_data_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

            # Write the output data to the file
            with open(output_file_path, 'w') as file:
                file.write(output_data)
                logging.info(f"All data saved to {output_file_path}.")

        else:
            logging.error("Failed to generate podcast script or title.")
    else:
        logging.error("Failed to identify top news.")
