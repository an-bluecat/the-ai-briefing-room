import openai
import requests
import base64

from openai import OpenAI
from dotenv import load_dotenv
import os

today_date = "2024-05-23"

output_directory = f'/output/{today_date}/'
# add today as file path of output_directory
os.makedirs(output_directory, exist_ok=True)