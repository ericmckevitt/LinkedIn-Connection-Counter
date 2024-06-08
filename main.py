import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup 
from lxml import etree

# Load from .env
import os
from dotenv import load_dotenv
load_dotenv()

# Get the username and password
username = os.getenv("LINKEDIN_USERNAME")
password = os.getenv("LINKEDIN_PASSWORD")

# Make a Chrome driver
driver = webdriver.Chrome(ChromeDriverManager().install())

# Get the page
driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')

# Wait for the page to load
driver.implicitly_wait(10)

driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[1]/input").click()
driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[1]/input").send_keys(username)

driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[2]/input").click()
driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[2]/input").send_keys(password)

driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[3]/button").click()

connection_count = driver.find_element(By.XPATH, "/html/body/div[4]/div[3]/div/div/div/div/div[2]/div/div/main/div/section/header/h1").text

print(f"Connection count: {connection_count}")

# Get the HTML
html = driver.page_source 

# Close the driver
driver.close()