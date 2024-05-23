import openai
import requests
import base64

from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()
# Set your OpenAI API key

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

prompt = '''
A cohesive podcast cover image featuring a nighttime scene of the Earth from space, with a focus on Indonesia illuminated by city lights. A sleek satellite in orbit, symbolizing Elon Musk's Starlink, beams a vibrant signal down to the Indonesian archipelago. In the foreground, a modern computer monitor with a holographic AI interface glows with dynamic data streams, representing Microsoft's AI integration. To the right, a stylish pair of wireless headphones from Sonos hovers, emitting colorful sound waves that blend into the background. The elements merge seamlessly, creating a unified, futuristic composition that highlights the innovation and connectivity of these tech advancements.'''

# Generate the image using DALL·E with the prompt and the encoded image
response = client.images.generate(
  model="dall-e-3",
  prompt=prompt,
  size="1024x1024",
  quality="standard",
  n=1,
)

# Get the URL of the generated image
image_url = response.data[0].url
print(f"Generated image URL: {image_url}")

# Download the image using the URL
image_response = requests.get(image_url)

# Check if the request was successful
if image_response.status_code == 200:
    with open('generated_image.png', 'wb') as file:
        file.write(image_response.content)
    print("Image downloaded successfully!")
else:
    print("Failed to download the image")
