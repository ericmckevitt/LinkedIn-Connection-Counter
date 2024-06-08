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