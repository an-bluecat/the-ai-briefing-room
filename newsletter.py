import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from openai import AzureOpenAI

TLDR_example = """
Sign Up |Advertise|View Online
TLDR

Together With Bland AI
TLDR AI 2024-04-26
AI phone calls?! The world's fastest conversational AI was released and it sounds just like a human (Sponsor)

AI lab, Bland AI has released a hyper-realistic sounding AI phone agent, and it's blowing everyone's minds.
It can be used for anything: sales, instantly calling and pre-qualifying leads, customer support…
It can handle over 1,000,000 business phone calls simultaneously.
It can respond at human level speeds... with any voice.
Developers and companies are loving this. Impacts on the job market are coming soon...

Skeptical? Try calling it yourself >> Bland.ai

(P.S. TLDR readers can sign up here and access something even crazier...)

🚀
Headlines & Launches
Snowflake Arctic - LLM for Enterprise AI (11 minute read)

The Snowflake AI Research Team has introduced Snowflake Arctic, an enterprise-grade LLM that delivers top-tier performance in SQL generation, coding, and instruction-following benchmarks at a fraction of traditional costs. Arctic leverages a unique architecture and an open-source approach, making advanced LLM capabilities accessible to a wider audience. The model is available on Hugging Face and will be integrated into various platforms and services.
Nvidia acquires AI workload management startup Run:ai for $700M (3 minute read)

Nvidia is acquiring AI infrastructure optimization firm Run:ai for approximately $700 million to enhance its DGX Cloud AI platform, allowing customers improved management of their AI workloads. The acquisition will support complex AI deployments across multiple data center locations. Run:ai had previous VC investments and a broad customer base, including Fortune 500 companies.
Apple Acquires French AI Company Specializing in On-Device Processing (3 minute read)

Apple has acquired Paris-based artificial intelligence startup Datakalab amid its push to deliver on-device AI tools. Datakalab specializes in algorithm compression and embedded AI systems.

Stop receiving emails here.
AlphaSignal, 214 Barton Springs RD, Austin, Texas 94123, United States
"""

MODEL = "GPT4"

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("API_VERSION")
)

def generate_newsletter(content):
    # role = f"You are a helpful podcast content summarizer. You need to summarize the podcast and decorate it in Markdown. \n\n You can reference this example but style it with markdown: \n\n{TLDR_example}\n"
    role = f"""You are a professional newsletter editor specialized in technology topics. Your task is to summarize the provided content into a concise, engaging, and informative markdown newsletter. The newsletter should be easy to read, include bullet points for key facts, subheadings for different sections, and incorporate a formal yet engaging tone. Use hyperlinks appropriately to encourage readers to engage further. Use combination of emoji. \n\n You can reference this example but style it with markdown {TLDR_example}"""


    prompt = f"Create a professional markdown newsletter style email summary for the podcast content: {content}"

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": role},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error while generating newsletter: {e}")
        return None

def send_email(subject, message, to_email, is_markdown=False):
    if message is None:
        print("No newsletter content to send.")
        return

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'aibriefingroom@gmail.com'
    smtp_password = 'dxlm tcut yvts czmt'

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

# Example usage
content = """Podcast Description:
tech briefing: unveiling today's critical updates - may 1

dive into the latest tech developments with our expert insights:

- unitedhealth group's cybersecurity breach: ceo andrew witty reveals a $22 million ransom payment following a significant attack on change healthcare. discover how this incident impacts data security and unitedhealth's plans to bolster its defenses.

- amazon under fire: ceo andy jassy's comments on unionization draw criticism from the nlrb, marking a pivotal moment in the company's labor relations. learn about the implications for amazon's work environment and legal standing.

- google's job cuts and reorganization: google announces job eliminations and relocations as part of a cost-cutting measure. understand the strategic motivations behind these moves and their impact on the tech giant's future.

- qualcomm's financial triumph: with a fiscal second-quarter report that surpasses expectations, qualcomm is on the rise. explore how a boost in handset sales and strategic focus on ai and automotive sectors are propelling qualcomm's success.

join us for a concise overview of these pivotal stories in the tech world, offering essential knowledge for anyone keeping pace with the rapidly evolving technological landscape
"""
title = "Unitedhealth's $22m Cyber Ransom 💻, Amazon's Union Controversy 🏢, Qualcomm's Ai Surge 📈"
newsletter_content = generate_newsletter(content)
send_email(title, newsletter_content, '1835928575qq@gmail.com', is_markdown=True)
