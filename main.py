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
from postProcess import add_bgm
from openai import AzureOpenAI
from utils import spanish_title_case
import sys


# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration constants
TEXT_MODEL = "GPT4"
MAX_RETRIES = 1
RETRY_DELAY = 2  # seconds in case of retries
PRODUCTION_MODE = True  # Set to True to enable audio file generation
BGM_PATH = "bgm.mp3"

class NewsPodcastOrchestrator:
    """ Orchestrates the creation of a podcast script from scraped news, using OpenAI's GPT models. """

    def __init__(self, api_key, date, news_to_URL):
        self.azure_client = AzureOpenAI(
        azure_endpoint =  os.getenv("AZURE_OPENAI_ENDPOINT"), 
        api_key= os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version=os.getenv("API_VERSION")
    )
        self.openai_client = openai.OpenAI(api_key=api_key)

        self.date = date
        self.news_to_URL = news_to_URL

    def ask_gpt(self, input_ask, role="system"):
        """ Sends a request to GPT model and handles retries if necessary. """
        attempts = 0
        while attempts < MAX_RETRIES:
            try:
                completion = self.azure_client.chat.completions.create(
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

    def translate_text(self, text, target_language):
        """ Translates text to the specified target language using the GPT model. """
        # first prompt:
        prompt = f"Translate the English part of the text to {target_language}. Do not translate word by word; Do Translation naturally:\n\n{text}\n Translation:"
        # second prompt:
        # prompt = f"Translate the English part of the text to {target_language}. Use your maximum effort to adjust the content to adapt for culture and language differences so that it flows the best. Remember to use your creativity to adjust the content for the best {target_language} experience::\n\n{text}\n Translation:"
        translation = self.ask_gpt(prompt)
        return translation

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

    def generate_podcast_script(self, news_concat, language=None):
        """ Generates a podcast script based on the top news titles. """
        output_response_prompt = ""
        if language:
            output_response_prompt = f"Output the response in {language}."
        first_shot = """
        Prompt: Give a quick tech news update script in the style of CNBC techcheck briefing as an example.
        Response: I'm Wall-E, and this is your CNBC techcheck Briefing. Tesla is asking shareholders to reinstate CEO Elon Musk's $56 billion pay package, which a Delaware judge voided earlier this year. The judge ruled that the record-setting compensation deal was, quote, deeply flawed. Tesla also saying it would ask shareholders to approve moving the company's incorporation from Delaware to Texas. The company has hired a proxy solicitor and plans to spend millions of dollars to help secure votes for the two proposals. Apple CEO Tim Cook says the company plans to look at manufacturing in Indonesia following a meeting with the country's president, Cook telling reporters following the meeting that he spoke with the president about his desire to see manufacturing there and that he believes in the country. The comments come as Apple is pushed to diversify its supply chain with more manufacturing outside of China in countries such as Vietnam and India. Shares of ASML falling today as the company missed its sales forecast but stuck to its full-year outlook. Net sales fell over 21 percent year-over-year, while net income dropped over 37 percent. ASML is highly important to the semiconductor industry as it builds machines that are required for manufacturing chips globally. Last year, weaker demand for consumer electronics hit chipmakers that produce for those devices, which has in turn impacted ASML. That's all for today. We'll see you back here tomorrow.
        """

        prompt = f"Prompt: Give a quick tech news update script in the style of CNBC techcheck briefing using the following news titles and content. Closely follow how CNBC techcheck chooses context to put into the script, the langauge style and sentence structure. Use the same beginning and ending(including host name), and replace CNBC techcheck briefing to 'AI briefing' \n {news_concat}\n" + \
            output_response_prompt + "\n"
        response_begin = "Response:"
        input_ask = first_shot + prompt + response_begin

        return input_ask, self.ask_gpt(input_ask)

    def get_news_content_concat(self, top_news):
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
        return news_concat

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

    def generate_podcast_description(self, script, language=None):
        """ Generates a podcast description from the provided script. """

        output_response_prompt = ""
        if language:
            output_response_prompt = f"Output the Description in {language}."

        input_ask = f"""
            Generate a description for this podcast. Summarize topics discussed. This will be the script we use for the podcast description on Apple Podcast. So please be concise, use bullet point when possible. Please use plain text, no markdown.
            Here's the podcast script: 
            "
            {script}
            "
            {output_response_prompt}
            Description:
            """

        return self.ask_gpt(input_ask)

    def text_to_speech(self, script, output_path, language='English'):
        """ Converts the generated script to speech and saves the audio file. Now supports multiple languages. """

        try:
            response = self.openai_client.audio.speech.create(
                model="tts-1", voice="alloy", input=script)
            speech_file_path = Path(
                output_path) / f"{language}.mp3"
            response.stream_to_file(speech_file_path)
            
            final_podcast_path = Path(output_path) / f"{language}_final_podcast.mp3"

                # Add BGM to the generated speech
            add_bgm(str(speech_file_path), BGM_PATH, str(final_podcast_path))
            
            os.remove(speech_file_path)

            logging.info(
                f"Generated {language} speech saved to {speech_file_path}.")
            return speech_file_path
        except Exception as e:
            logging.error(f"Failed to convert text to speech: {e}")
            return None

    def generate_podcast_title(self, transcript, language=None):
        """ Generates a podcast title from the provided transcript. """
        output_response_prompt = ""
        if language:
            output_response_prompt = f"Output the Title in {language}."
        input_ask = "Generate a title for this podcast. Include no more than three key topics (if there are many, choose the three most important ones). Incorporate emojis where appropriate. Follow the style of titles such as: 'Tesla Showcases FSD Demo 🚗, Adam Neuman's WeWork Bid 💰, CSV Conundrums 🖥️','Anthropic’s $4B Amazon Boost 💰, Brex's Valuation Leap to $12B 💳, Strategies for Success ✨','The OpenAI Voice Revolution 🗣️, AI Safety Measures 🦺, LLMs Go Mobile 📱'. Here's the transcript excerpt: " + transcript + "\n" + output_response_prompt + "\nTitle:"
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
    #api_key = os.getenv('AZURE_OPENAI_API_KEY')

    today = datetime.date.today()
    today_date = today.strftime('%Y-%m-%d')
    
    if len(sys.argv) > 1:
        episode_prefix = sys.argv[1]
        episode_number = f"EP-{episode_prefix} "
        print(episode_number)
    else:
        raise ValueError("No additional argument provided.")
    
    all_news = scrape_verge(
        today) + scrape_cnbctech(today) + scrape_techcrunch(today)

    titles = [x[0] for x in all_news]
    news_to_URL = {news[0].lower(): news[1] for news in all_news}

    output_directory = f'./output/{today_date}/'
    # add today as file path of output_directory
    os.makedirs(output_directory, exist_ok=True)

    orchestrator = NewsPodcastOrchestrator(api_key, today, news_to_URL)

    top_news_prompt, top_news = orchestrator.get_top_news()
    news_concat = orchestrator.get_news_content_concat(
        remove_leading_numbers(top_news))
    if top_news:
        generate_script_prompt, script = orchestrator.generate_podcast_script(
            news_concat)

        polished_script = orchestrator.polish_podcast_script(script)
        podcast_description = orchestrator.generate_podcast_description(
            polished_script)
        podcast_title = episode_number +  orchestrator.generate_podcast_title(polished_script).title()
        TRANSLATE = False
        if TRANSLATE:
            # Translate the polished script, description, and title to Spanish and Chinese
            spanish_script = orchestrator.translate_text(
                polished_script, "Spanish")
            spanish_description = orchestrator.translate_text(
                podcast_description, "Spanish")
            spanish_title = episode_number + spanish_title_case(spanish_title_case(orchestrator.translate_text(
                podcast_title, "Spanish")))

            chinese_script = orchestrator.translate_text(
                polished_script, "Chinese")
            chinese_description = orchestrator.translate_text(
                podcast_description, "Chinese")
            chinese_title = episode_number +  orchestrator.translate_text(
                podcast_title, "Chinese")
        else:
            _, spanish_script = orchestrator.generate_podcast_script(
                news_concat, language="Spanish")
            _, chinese_script = orchestrator.generate_podcast_script(
                news_concat, language="Chinese")
            spanish_description = orchestrator.generate_podcast_description(
                spanish_script, language="Spanish")
            chinese_description = orchestrator.generate_podcast_description(
                chinese_script, language="Chinese")
            spanish_title = episode_number + spanish_title_case(orchestrator.generate_podcast_title(
                spanish_script, language="Spanish"))
            chinese_title = episode_number +  orchestrator.generate_podcast_title(
                chinese_script, language="Chinese")

            # Text to Speech for each language, including the original English
        if PRODUCTION_MODE:
            for language, cur_script in [('English', polished_script), ('Spanish', spanish_script), ('Chinese', chinese_script)]:
                audio_file_path = orchestrator.text_to_speech(
                    cur_script, output_directory, language)
                if audio_file_path:
                    logging.info(
                        f"Podcast in {language} completed successfully. Audio file at: {audio_file_path}")
                else:
                    logging.error(f"Failed to generate {language} audio file.")

            # Prepare the output text data
            # output_data = f"Titles:\n{chr(10).join(titles)}\n\ntop_news_prompt: {top_news_prompt}\n\nTop News:\n{chr(10).join(top_news)}\n\nGenerate_scipt_prompt:\n{generate_script_prompt}\n\nScript:\n{script}\n\npolished_script:\n{polished_script}\n\nPodcast Title:\n{podcast_title}\n\npodcast_description:\n{podcast_description}\n"
            output_data = f"""
Titles:
{chr(10).join(titles)}

top_news_prompt: {top_news_prompt}

Top News:
{chr(10).join(top_news)}

Generate_script_prompt:
{generate_script_prompt}

Script:
{script}

Polished Script:
{polished_script}

Podcast Title:
{podcast_title}

Podcast Description:
{podcast_description}

Polished Script (Spanish):
{spanish_script}

Podcast Title (Spanish):
{spanish_title}

Podcast Description (Spanish):
{spanish_description}

Polished Script (Chinese):
{chinese_script}

Podcast Title (Chinese):
{chinese_title}

Podcast Description (Chinese):
{chinese_description}
"""
            output_file_path = f"{output_directory}podcast_data.txt"

            # Write the output data to the file
            with open(output_file_path, 'w') as file:
                file.write(output_data)
                logging.info(f"All data saved to {output_file_path}.")

        else:
            logging.error("Failed to generate podcast script or title.")
    else:
        logging.error("Failed to identify top news.")



