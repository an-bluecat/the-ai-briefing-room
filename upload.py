from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv

load_dotenv()
url = "https://podcasters.spotify.com/pod/dashboard/home"
email= os.getenv("EMAIL")
password = os.getenv("PASSWORD")

webdriver_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=webdriver_service)
driver.get(url)

# Click the "Continue with Spotify" button
continue_with_spotify_button =  WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[span[contains(text(), "Continue with Spotify")]]')))
continue_with_spotify_button.click()

# Log in
email_field =  WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "login-username")))
password_field = driver.find_element(By.ID, "login-password")
email_field.send_keys(email)
password_field.send_keys(password)
login_button = driver.find_element(By.ID, "login-button")
login_button.click()

# Continue to App
continue_to_app_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//*[@id='encore-web-main-content']/div/main/section/div/div/button/span[1]"))
)
continue_to_app_button.click()
time.sleep(5)

# new episode
current_url = driver.current_url
driver.get("https://podcasters.spotify.com/pod/dashboard/episode/wizard")
time.sleep(5)

# upload file
file_path = "output/2024-04-24/English_final_podcast.mp3"
current_dir = os.getcwd()  
absolute_path = os.path.join(current_dir, file_path)
file_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
)
file_input.send_keys(absolute_path)
time.sleep(3)

# Details
title_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "title"))  
)
title_input.send_keys('Your Podcast Title')

description_input = driver.find_element(By.NAME, "description")
description_input.send_keys('Your Podcast Description')

publish_now_radio = driver.find_element(By.ID, "publish-date-now")
driver.execute_script("arguments[0].click();", publish_now_radio)
no_explicit_content_radio = driver.find_element(By.ID, "no-explicit-content")
driver.execute_script("arguments[0].click();", no_explicit_content_radio)
no_promotional_radio = driver.find_element(By.ID, "no-sponsored-content")
driver.execute_script("arguments[0].click();", no_promotional_radio)
time.sleep(5)
footer = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.TAG_NAME, "footer"))
)
driver.execute_script("arguments[0].scrollIntoView();", footer)
next_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Next']]"))
)
next_button.click()
time.sleep(3)

# Interact
next_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Next']]"))
)
next_button.click()
time.sleep(3)
