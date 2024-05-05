# the-ai-briefing-room

![Design Diagram](design_diagram.jpg)

### Installation

First, ensure you have Python installed on your system. Then, install the required dependencies:

`pip install -r requirements.txt`

### Running the Script
To generate a podcast episode, use the following command:

`python main.py [episode number]`

Replace [episode number] with the actual number of the episode you want to generate.

### Output
After running the script, the output will be organized into folders by date within the output folder. Each folder will contain three .mp3 files for the podcast in different languages (Chinese, English, Spanish) and a .txt file containing the podcast title, description, and script. See the example structure below:
```
/output
  /2024-04-23
    Chinese_final_podcast.mp3
    English_final_podcast.mp3
    Spanish_final_podcast.mp3
    podcast_data.txt
```


### Configuration
1. Create a `.env` file in the root directory of your project and add the following content:

```
AZURE_OPENAI_API_KEY = [your Azure key]
AZURE_OPENAI_ENDPOINT = [your Azure password]
API_VERSION = "2024-02-01"
EMAIL = [anchor login email]
PASSWORD = [anchor login password]
```

Replace [xxx] with your actual credentials

2. Create a JSON file named `ai-briefing-room-key.json` with obfuscated details for sensitive fields:
```
{
    "type": "service_account",
    "project_id": "YOUR_PROJECT_ID",
    "private_key_id": "YOUR_PRIVATE_KEY_ID",
    "private_key": "YOUR_PRIVATE_KEY",
    "client_email": "YOUR_CLIENT_EMAIL",
    "client_id": "YOUR_CLIENT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/YOUR_CLIENT_EMAIL",
    "universe_domain": "googleapis.com"
}
```

