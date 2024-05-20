import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from openai import OpenAI
import re
from dotenv import load_dotenv
from pathlib import Path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent


TLDR_EXAMPLE = ""
with open(current_dir / "newsletter.md", 'r', encoding='utf-8') as file:
    TLDR_EXAMPLE = file.read()

TLDR_TITLE_EXAMPLE = ""
with open(current_dir / "newsletter_title.md", 'r', encoding='utf-8') as file:
    TLDR_TITLE_EXAMPLE = file.read()

MODEL = "GPT4"

load_dotenv()

client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY"),
    organization = os.getenv('OPENAI_ORGANIZATION_ID')
)

def generate_newsletter(content:str)->str:
    # role = f"You are a helpful podcast content summarizer. You need to summarize the podcast and decorate it in Markdown. \n\n You can reference this example but style it with markdown: \n\n{TLDR_example}\n"
    role = f"""You are a professional newsletter editor specialized in technology topics. Your task is to summarize the provided content into a concise, engaging, and informative markdown newsletter. The newsletter should be easy to read, include bullet points for key facts, subheadings for different sections, and incorporate a formal yet engaging tone. Use hyperlinks appropriately to encourage readers to engage further. Use combination of emoji. \n\n You can reference this example but style it with markdown {TLDR_EXAMPLE}"""


    prompt = f"Create a professional markdown newsletter style email summary for the podcast content: {content}"

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": role},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0
        )
        return completion.choices[0].message
    except Exception as e:

        print(f"Error while generating newsletter title: {e}")
        return None

def send_email(subject:str, message:str, to_email, is_markdown=False)->None:
    if message is None:
        print("No newsletter content to send.")
        return

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'aibriefingroom@gmail.com'
    smtp_password = os.getenv("SMTP_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject
    if is_markdown:
        from markdown import markdown
        message = markdown(message)
    msg.attach(MIMEText(message, 'html' if is_markdown else 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Database

import sqlite3
# Database functions
def init_db() -> None:
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            email TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def add_subscriber(email:str) -> None:
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Email already exists in the database.")
    conn.close()

def get_subscribers() -> list[str]:
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('SELECT email FROM subscribers')
    emails = c.fetchall()
    conn.close()
    return [email[0] for email in emails]

# Google sheet
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to your downloaded service account key file
SERVICE_ACCOUNT_FILE = 'ai-briefing-room-key.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def google_sheets_service():
    """Creates a Google Sheets service client using service account credentials."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def get_subscribers(service):
    """Retrieves subscriber emails from a specific Google Sheets range."""
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    RANGE_NAME = 'response!B2:B'  # Make sure to adjust the sheet name and range as necessary
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])
    return [row[0] for row in rows if row]

def format_newsletter(content: str)->tuple[str, str]:
    newsletter_content = generate_newsletter(content).content
    while not newsletter_content or len(newsletter_content) < 200:#too short
        newsletter_content = generate_newsletter(content).content
    newsletter_content = "###" + "###".join(newsletter_content.split("###")[1:]).split("---")[0] # remove title and intro, and summary at the end
    newsletter_content += "\n\n[🔊 Listen to the Full Podcast Episode Here](https://podcasters.spotify.com/pod/show/aibriefingroom)"
    return newsletter_content

def send_newsletter(title:str, newsletter_content:str,  use_sheet = True, test = False) -> None:
    if test:
        subscribers = ['1835928575qq@gmail.com'] # testing purpose
    elif use_sheet:
      service = google_sheets_service()
      subscribers = get_subscribers(service)
    else:
      init_db()
      subscribers = get_subscribers()  # Retrieve all subscribers

    for email in subscribers:
        send_email(title, newsletter_content, email, is_markdown=True)
        print(email)

def extract_title_and_description(file_path: str|None=None, content: str|None = None) -> str:
    if file_path is not None:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

    if content is None:
        raise ValueError("Either file_path or content should be provided.")

    title, description = "", ""
    # Use regex to find the podcast description
    description_match = re.search(r"Podcast Description:\n(.*?)\nPolished Script \(Spanish\):", content, re.DOTALL)
    if description_match:
        description = description_match.group(1).strip()
    
    # Use regex to find the podcast title
    title_match = re.search(r"Podcast Title:\n(.*?)\nPodcast Description:", content, re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
    
    if title and description:
        return title, content
    else:
        raise ValueError("Podcast description or title not found in the content.")

if __name__ == "__main__":
    file_path = parent_dir / "output/2024-05-20/podcast_data.txt"
    title, content = extract_title_and_description(file_path=file_path)
    send_newsletter(title, format_newsletter(content),use_sheet=True, test=True)