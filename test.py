import openai
import requests
import base64

from openai import OpenAI
from dotenv import load_dotenv
import os
from utils.utils import spanish_title_case, english_title_case


print(english_title_case("🔜 Nvidia’s new annual ai chip rollout 🧠, Amazon alexa’s ai overhaul with subscription 🎙️, microsoft ties executive pay to cybersecurity 💼"))