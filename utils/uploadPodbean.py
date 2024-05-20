import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

load_dotenv()

# Replace with your actual client ID, client secret, and access token
CLIENT_ID = os.getenv("PODBEAN_CLIENT_ID")
CLIENT_SECRET = os.getenv("PODBEAN_CLIENT_SECRET")
FILE_NAME = "../output/2024-05-16/English_final_podcast.mp3"
USER_AGENT = 'MyClientApp/1.0'  # Replace with your actual application name and version

# Episode details
TITLE = "Good fdsday"
CONTENT = "Time you <b>enjoy</b> wasting, wdsfas not wasted."
STATUS = "draft"
TYPE = "public"

# Step 1: Obtain OAuth token
def get_oauth_token(client_id, client_secret):
    url = 'https://api.podbean.com/v1/oauth/token'
    data = {'grant_type': 'client_credentials'}
    headers = {'User-Agent': USER_AGENT}
    response = requests.post(url, data=data, auth=HTTPBasicAuth(client_id, client_secret), headers=headers)

    if response.status_code == 200:
        token_info = response.json()
        return token_info['access_token'].strip()
    else:
        print("Failed to retrieve token:", response.status_code, response.text)
        return None

# Step 2: Get file size
def get_file_size(filename):
    return os.path.getsize(filename)

# Step 3: Get upload authorization and extract file key
def get_upload_authorization(access_token, filename):
    url = 'https://api.podbean.com/v1/files/uploadAuthorize'
    
    current_dir = os.getcwd()
    absolute_path = os.path.join(current_dir, filename)
    if not os.path.isfile(absolute_path):
        print(f"File not found: {absolute_path}")
        return None
    
    filesize = get_file_size(absolute_path)
    params = {
        'access_token': access_token,
        'filename': os.path.basename(filename),
        'filesize': filesize,
        'content_type': 'audio/mpeg'
    }
    headers = {'User-Agent': USER_AGENT}

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        upload_info = response.json()
        return upload_info.get('file_key')
    else:
        print("Failed to get upload authorization:", response.status_code, response.text)
        return None

# Step 4: Publish episode
def publish_episode(access_token, title, content, status, type_, media_key):
    url = 'https://api.podbean.com/v1/episodes'
    headers = {
        'User-Agent': USER_AGENT,
    }
    data = {
        'access_token': access_token,
        'title': title,
        'content': content,
        'status': status,
        'type': type_,
        'media_key': media_key
    }

    response = requests.post(url, headers=headers, data=data)

    print("Request URL:", response.url)
    print("Response Status Code:", response.status_code)
    print("Response Text:", response.text)

    if response.status_code == 200:
        episode_info = response.json()
        print("Episode Published:", episode_info)
    else:
        print("Failed to publish episode:", response.status_code, response.text)

if __name__ == '__main__':
    access_token = get_oauth_token(CLIENT_ID, CLIENT_SECRET)
    if access_token:
        media_key = get_upload_authorization(access_token, FILE_NAME)
        if media_key:
            publish_episode(access_token, TITLE, CONTENT, STATUS, TYPE, media_key)
