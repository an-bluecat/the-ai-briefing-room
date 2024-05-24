import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from openai import OpenAI
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
from pathlib import Path
import mimetypes

newsLetter_dir = Path(__file__).parent
root_dir = newsLetter_dir.parent


NEWSLETTER_EXAMPLE = ""
with open(newsLetter_dir / "newsletter.md", 'r', encoding='utf-8') as file:
    NEWSLETTER_EXAMPLE = file.read()

TLDR_TITLE_EXAMPLE = ""
with open(newsLetter_dir / "newsletter_title.md", 'r', encoding='utf-8') as file:
    TLDR_TITLE_EXAMPLE = file.read()

MODEL = "GPT4"

load_dotenv()

client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY"),
    organization = os.getenv('OPENAI_ORGANIZATION_ID')
)

# Deprecated function due to we are keeping the newsletter title same as the podcast title

# def generate_newsletter_title(content:str)->str:
#     role = f"""
#     You are a professional newsletter title generator specialized in technology topics. Your task is to generate the overall title based on the newsletter. The title of the newsletter should be 1 line only, easy to read, include bullet points for key facts. Use a combination of emoji.
#     You can reference this example but style it with markdown {{TLDR_TITLE_EXAMPLE}}. You must generate only 1 line title because the title should be concise enough."""

#     prompt = f"Create a professional title in newsletter style for the podcast content: {content}"
#     try:
#         completion = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": role},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=100,
#             temperature=0.7,
#             top_p=0.95,
#             frequency_penalty=0,
#             presence_penalty=0
#         )
#         return completion.choices[0].message
#     except Exception as e:

#         print(f"Error while generating newsletter title: {e}")
#         return None

def generate_html_content(heading, greeting, content)->str:
    from markdown import markdown
    html_content = markdown(content)
    html_greeting = markdown(greeting)
    return f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                color: #333;
                background-color: #f4f4f9;
                padding: 20px;
            }}
            .header {{
                background-color: #1a73e8;
                color: white;
                padding: 10px;
                border-radius: 10px;
            }}
            .heading {{
                text-align: center;
            }}
            .content {{
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                color: #666;
            }}
            .social-icons img {{
                width: 24px;
                margin: 0 5px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 class="heading">{heading}</h1>
            <p>{html_greeting}</p>
        </div>
        <div class="content">
            {html_content}
        </div>
        <div class="footer">
            <p>Follow us on:</p>
            <div class="social-icons">
                <img src="cid:icon_facebook" alt="Facebook" />
                <img src="cid:icon_linkedin" alt="LinkedIn" />
            </div>
            <p>Contact us at: aibriefingroom@gmail.com</p>
        </div>
    </body>
    </html>
    """

def generate_newsletter(content:str)->str:
    # role = f"You are a helpful podcast content summarizer. You need to summarize the podcast and decorate it in Markdown. \n\n You can reference this example but style it with markdown: \n\n{TLDR_example}\n"
    role = f"""You are a professional newsletter editor specialized in technology topics. Given the script of a tech podcast and its description, your task is to summarize the provided content into a concise, engaging, and informative markdown newsletter. The newsletter should be easy to read, include bullet points for key facts, subheadings for different sections, and incorporate a formal yet engaging tone. Use hyperlinks appropriately to encourage readers to engage further. Use combination of emoji. Assume that we already wrote the welcome message is already written for you so you can start straight from content.\n\n  You must strictly follow the format of this example: {NEWSLETTER_EXAMPLE}"""


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

        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error while generating newsletter title: {e}")
        return None

def send_email(subject:str, message:str, to_email, is_markdown=True)->None:
    if message is None:
        print("No newsletter content to send.")
        return

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'aibriefingroom@gmail.com'
    smtp_password = os.getenv("SMTP_PASSWORD")

    msg_root = MIMEMultipart('related')
    msg_root['From'] = smtp_username
    msg_root['To'] = to_email
    msg_root['Subject'] = subject

    msg_alternative = MIMEMultipart('alternative')
    msg_root.attach(msg_alternative)

    if is_markdown:
        greeting = "## Hey friend,\n### Welcome to today's edition of AI Briefing Room.\n### Let's dive into it!"
        print('Generating HTML content...')
        message = generate_html_content(heading="Wall-E's Tech Briefing", greeting=greeting, content=message)
        msg_alternative.attach(MIMEText(message, 'html'))
        assets_dir = root_dir / 'assets'
        image_files = {
            'icon_facebook': assets_dir / 'fb.svg',
            'icon_linkedin': assets_dir / 'in.svg',
        }
        for cid, file_path in image_files.items():
            with open(file_path, 'rb') as img_file:
                img_data = img_file.read()
                mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type is None:
                    raise TypeError(f'Could not guess image MIME subtype for {file_path}')
                _, subtype = mime_type.split('/')
                img = MIMEImage(img_data, _subtype=subtype)
                img.add_header('Content-ID', f'<{cid}>')
                img.add_header('Content-Disposition', 'inline', filename=Path(file_path).name)
                msg_root.attach(img)
    else:
        msg_root.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to_email, msg_root.as_string())
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
    RANGE_NAME = 'response!B2:B'
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])
    return [row[0] for row in rows if row]

def format_newsletter(content: str)->tuple[str, str]:
    newsletter_content = generate_newsletter(content)
    # remove title and intro, and summary at the end
    # newsletter_content = "###" + "###".join(newsletter_content.split("###")[1:]).split("---")[0]
    # title = generate_newsletter_title(newsletter_content).content.lstrip("#")
    newsletter_content += "Stay informed with Wall-E's tech updates, and see you back here tomorrow!\n\n---\n\n[🔊 Listen to the Full Podcast Episode Here](https://podcasters.spotify.com/pod/show/aibriefingroom)"
    return newsletter_content


TEST = False
TEST_EMAIL = '1835928575qq@gmail.com'

def send_newsletter(newsletter_content:str, title:str, use_sheet = True, test = False) -> None:
    if test:
        subscribers = [TEST_EMAIL] # testing purpose
    elif use_sheet:
      service = google_sheets_service()
      subscribers = get_subscribers(service)
    else:
      init_db()
      subscribers = get_subscribers()  # Retrieve all subscribers

    for email in subscribers:
        send_email(title, newsletter_content, email, is_markdown=True)
        print(email)

if __name__ == "__main__":
    yesterday = datetime.now() - timedelta(days=1)
    formatted_date = yesterday.strftime('%Y-%m-%d')
    # Path to your file, should keep it updated
    with open(root_dir / 'output' / formatted_date / 'podcast_data.json', 'r') as file:
        data = json.load(file)
        title, description, script = data['Podcast Title'], data['Podcast Description'], data['Polished Script']

    newsletter_content = format_newsletter(f'Podcast Description: {description}\n Podcast Script: {script}')
    send_newsletter(newsletter_content, title, use_sheet=True, test=TEST)