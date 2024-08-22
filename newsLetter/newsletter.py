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
from copy import deepcopy
import base64

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

def encode_image_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def generate_html_content(heading, date, content)->str:
    from markdown import markdown
    html_content = markdown(content)

    # Base64 encoding images
    assets_dir = root_dir / 'assets'
    fb_image_base64 = encode_image_to_base64(assets_dir / 'fb.png')
    linkedin_image_base64 = encode_image_to_base64(assets_dir / 'in.png')

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
                text-align: center;
                background-color: #1a73e8;
                color: white;
                padding: 10px;
                border-radius: 10px;
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
            <h1>{heading}</h1>
            <h3>{date}</h3>
        </div>
        <div class="content">
            {html_content}
        </div>
        <!-- <div class="footer">
            <p>Follow us on:</p>
            <div class="social-icons">
                <img src="data:image/png;base64,{fb_image_base64}" alt="Facebook" />
                <img src="data:image/png;base64,{linkedin_image_base64}" alt="LinkedIn" />
            </div>
            <p>Contact us at: aibriefingroom@gmail.com</p>
        </div> -->
    </body>
    </html>
    """

def generate_newsletter(content:str)->str:
    # role = f"You are a helpful podcast content summarizer. You need to summarize the podcast and decorate it in Markdown. \n\n You can reference this example but style it with markdown: \n\n{TLDR_example}\n"
    role = f"""You are a professional newsletter editor specialized in technology topics. Given the script of a tech podcast and its description, your task is to summarize the provided content into a concise, engaging, and informative markdown newsletter. The newsletter should be easy to read, include bullet points for key facts, subheadings for different sections, and incorporate a formal yet engaging tone. Use hyperlinks appropriately to encourage readers to engage further. Use combination of emoji. Assume that we already wrote the welcome message is already written for you so you can start straight from content. Do not generate the footer neither.\n\n  You must strictly follow the format of this example: {NEWSLETTER_EXAMPLE}"""


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

def send_email(prepared_msg: MIMEMultipart, to_email: str) -> None:
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = os.getenv("EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    msg = deepcopy(prepared_msg)
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully to", to_email)
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def prepare_email(subject: str, message: str, is_markdown=True) -> MIMEMultipart:
    smtp_username = os.getenv("EMAIL")

    msg_root = MIMEMultipart('related')
    msg_root['From'] = smtp_username
    msg_root['Subject'] = subject

    msg_alternative = MIMEMultipart('alternative')
    msg_root.attach(msg_alternative)

    if is_markdown:
        msg_alternative.attach(MIMEText(message, 'html'))
    else:
        msg_root.attach(MIMEText(message, 'plain'))

    return msg_root

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
SERVICE_ACCOUNT_INFO = json.loads(os.getenv('GOOGLE_KEY'))
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def google_sheets_service():
    """Creates a Google Sheets service client using service account credentials."""
    creds = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO, scopes=SCOPES)
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
    newsletter_content += "Stay informed with Wall-E's tech updates, and see you back here tomorrow!\n\n---\n\n[🔊 Listen to the Full Podcast Episode Here](https://aibriefingroom.podbean.com/)"
    return newsletter_content

def email_exists(service, email: str) -> bool:
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    RANGE_NAME = 'response!B:B'  # Assuming email is in column B

    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()

    emails = result.get('values', [])
    emails_flat = [email_row[0] for email_row in emails if email_row]  # Flatten the list
    return email in emails_flat

def signup_newsletter(service, name: str, email: str, preferences: list, ) -> None:
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    RANGE_NAME = 'response!A:D'

    # Prepare the values to be appended
    date = datetime.now().strftime('%m/%d/%Y')
    values = [[date, email, name, ', '.join(preferences)]]
    body = {'values': values}
    result = service.spreadsheets().values().append(
        spreadsheetId = SPREADSHEET_ID, 
        range=RANGE_NAME, 
        valueInputOption='RAW', 
        insertDataOption="INSERT_ROWS", 
        body=body
    ).execute()

    print(f"Added {name} to the newsletter list...")

def unsubscribe_user(service, email: str) -> bool:
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    RANGE_NAME = 'response!B:E'  # Assuming email is in column B and unsubscribed is in column E

    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()

    values = result.get('values', [])
    
    for idx, row in enumerate(values):
        if len(row) > 0 and row[0] == email:
            # If the email matches, update the 5th column (unsubscribed) with "True"
            cell_range = f'response!E{idx + 1}'
            update_body = {
                "values": [["True"]]
            }
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=cell_range,
                valueInputOption="USER_ENTERED",
                body=update_body
            ).execute()
            return True
    
    return False

TEST = False
TEST_EMAIL = '1835928575qq@gmail.com'

def send_newsletter(newsletter_content:str, subject:str, use_sheet = True, test = False) -> None:
    if test:
        subscribers = [TEST_EMAIL] # testing purpose
    elif use_sheet:
      service = google_sheets_service()
      subscribers = get_subscribers(service)
    else:
      init_db()
      subscribers = get_subscribers()  # Retrieve all subscribers

    print(f'Generated newsletter content...')
    date = datetime.now().strftime('%m/%d/%Y')  # You can set a common greeting here if needed
    html_content = generate_html_content(
        heading=f"Wall-E's Tech Briefing",
        date=date,
        content=newsletter_content
    )

    # Prepare the email content once
    prepared_msg = prepare_email(subject, html_content, is_markdown=True)


    for email in subscribers:
        send_email(prepared_msg, email)

        # Only print the email if it is a test
        if test:
            print(email)

if __name__ == "__main__":

    previous_day = datetime.now() - timedelta(days=3) if datetime.now().weekday() == 0 else datetime.now() - timedelta(days=1)
    formatted_date = previous_day.strftime('%Y-%m-%d')
    # Path to your file, should keep it updated
    with open(root_dir / 'output' / formatted_date / 'podcast_data.json', 'r') as file:
        data = json.load(file)
        subject, description, script = data['Podcast Title'], data['Podcast Description'], data['Polished Script']

        # Remove the episode prefix from the title
        import re
        pattern = r"EP-\d+ "
        subject = re.sub(pattern, "", subject)


    if TEST:
        newsletter_content = """sumary_line"""
    else:
        newsletter_content = format_newsletter(f'Podcast Description: {description}\n Podcast Script: {script}')

    send_newsletter(newsletter_content, subject, use_sheet=True, test=TEST)