import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup 
from lxml import etree
import os
from dotenv import load_dotenv
import sqlite3
import datetime

def login_to_linkedin(driver: webdriver.Chrome, username: str, password: str) -> None:
    driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    driver.implicitly_wait(10)
    
    # Enter login credentials and click login
    driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[1]/input").click()
    driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[1]/input").send_keys(username)

    driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[2]/input").click()
    driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[2]/input").send_keys(password)

    driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[3]/button").click()

def get_connection_count(driver: webdriver.Chrome, username: str, password: str) -> int:
    login_to_linkedin(driver, username, password)
    connection_count = driver.find_element(By.XPATH, "/html/body/div[4]/div[3]/div/div/div/div/div[2]/div/div/main/div/section/header/h1").text
    return int(connection_count.split(" ")[0].replace(",", ""))

def get_credentials() -> tuple[str, str]:
    load_dotenv()
    username = os.getenv("LINKEDIN_USERNAME")
    password = os.getenv("LINKEDIN_PASSWORD")
    return username, password

def connect_to_db():
    conn = sqlite3.connect('linkedin.db')
    c = conn.cursor()
    
    # Create connections table if it doesn't exist with the following columns: date, connection_count
    c.execute('''CREATE TABLE IF NOT EXISTS connections
                 (date text, connection_count integer)''')

    return conn, c

def clear_db():
    conn, c = connect_to_db()
    c.execute("DROP TABLE connections")
    conn.commit()

if __name__ == "__main__":
    username, password = get_credentials()
    
    # Make a Chrome driver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    connection_count = get_connection_count(driver, username, password)
    print(f"Connection count: {connection_count}")

    # Get the HTML
    html = driver.page_source 

    # Close the driver
    driver.close()

    # Get the date
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    conn, c = connect_to_db()
    c.execute("INSERT INTO connections VALUES (?, ?)", (today, connection_count))

    # Select all from the connections table
    c.execute("SELECT * FROM connections")
    
    snapshot = c.fetchall()
    print(snapshot)

    conn.commit()