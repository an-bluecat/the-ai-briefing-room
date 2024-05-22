import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

load_dotenv()

USER_AGENT = 'MyClientApp/1.0'

# Episode details
TITLE = "Good fdsday"  # title
CONTENT = "Time you <b>enjoy</b> wasting, wdsfas not wasted."  # description
STATUS = "draft"
TYPE = "public"
FILE_NAME = "output/2024-05-16/English_final_podcast.mp3"

def upload_podcast_episode(client_id, client_secret, file_name, title, content, status, type_, episode_number=None, publish_timestamp=None):
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

    # Step 3: Get upload authorization and presigned URL
    def get_upload_authorization(access_token, filename):
        url = 'https://api.podbean.com/v1/files/uploadAuthorize'
        
        absolute_path = os.path.abspath(filename)
        #print(f"Absolute File Path: {absolute_path}")
        
        if not os.path.isfile(absolute_path):
            print(f"File not found: {absolute_path}")
            return None, None
        
        filesize = get_file_size(absolute_path)
        params = {
            'access_token': access_token,
            'filename': os.path.basename(absolute_path),
            'filesize': filesize,
            'content_type': 'audio/mpeg'
        }
        headers = {'User-Agent': USER_AGENT}

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            upload_info = response.json()
        #    print("Upload Authorization Info:", upload_info)
            return upload_info.get('presigned_url'), upload_info.get('file_key')
        else:
            print("Failed to get upload authorization:", response.status_code, response.text)
            return None, None

    # Step 4: Upload file using presigned URL
    def upload_file_to_presigned_url(presigned_url, filename):
        headers = {'Content-Type': 'audio/mpeg'}
        with open(filename, 'rb') as f:
            response = requests.put(presigned_url, data=f, headers=headers)
        if response.status_code == 200:
            print("File successfully uploaded.")
            return True
        else:
            print("Failed to upload file:", response.status_code, response.text)
            return False

    # Step 5: Publish episode
    def publish_episode(access_token, title, content, status, type_, media_key, episode_number=None, publish_timestamp=None):
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
            'media_key': media_key,
            'episode_number':  episode_number,
            'publish_timestamp': publish_timestamp
        }
        
        print("Publishing Episode:", data)

        response = requests.post(url, headers=headers, data=data)

     #  print("Request URL:", response.url)
     #   print("Response Status Code:", response.status_code)
     #   print("Response Text:", response.text)

        if response.status_code == 200:
            episode_info = response.json()
            print("Episode Published:", episode_info)
        else:
            print("Failed to publish episode:", response.status_code, response.text)

    access_token = get_oauth_token(client_id, client_secret)
    if access_token:
        presigned_url, media_key = get_upload_authorization(access_token, file_name)
        if presigned_url and media_key:
            if upload_file_to_presigned_url(presigned_url, file_name):
                publish_episode(access_token, title, content, status, type_, media_key, episode_number, publish_timestamp)

if __name__ == '__main__':
    CLIENT_ID = os.getenv("PODBEAN_CLIENT_ID")
    CLIENT_SECRET = os.getenv("PODBEAN_CLIENT_SECRET")
    
    upload_podcast_episode(CLIENT_ID, CLIENT_SECRET, FILE_NAME, TITLE, CONTENT, STATUS, TYPE, 24, 1670000000)
