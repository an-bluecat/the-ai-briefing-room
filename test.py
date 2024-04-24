from newsplease import NewsPlease
from newsScraper import scrape_verge, scrape_cnbctech, scrape_techcrunch, scrape_and_group_by_source, format_grouped_titles_by_source, select_events_by_source
import datetime
import os
import requests
from dotenv import load_dotenv

load_dotenv()


azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')

# Your deployment name
deployment_name = 'tts-1'

# URL for the request
url = f"{azure_endpoint}/openai/deployments/{deployment_name}/audio/speech?api-version=2024-02-15-preview"

# Headers and data payload
headers = {
    "api-key": azure_api_key,
    "Content-Type": "application/json"
}
data = {
    "model": "tts-1-hd",
    "input": "I'm excited to try text to speech.",
    "voice": "alloy"
}

# Sending POST request
response = requests.post(url, headers=headers, json=data)

# Saving the response content to a file
with open('speech.mp3', 'wb') as file:
    file.write(response.content)

print("Audio file saved as 'speech.mp3'")