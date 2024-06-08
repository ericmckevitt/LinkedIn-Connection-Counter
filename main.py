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
import matplotlib.pyplot as plt

def login_to_linkedin(driver: webdriver.Chrome, username: str, password: str) -> None:
    """
    Logs into LinkedIn using the given username and password
    """
    driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    driver.implicitly_wait(10)
    
    # Enter login credentials and click login
    driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[1]/input").click()
    driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[1]/input").send_keys(username)

    driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[2]/input").click()
    driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[2]/input").send_keys(password)

    driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[3]/button").click()

def get_connection_count(driver: webdriver.Chrome, username: str, password: str) -> int:
    """
    Logs into LinkedIn and returns the number of connections
    """

    login_to_linkedin(driver, username, password)
    connection_count = driver.find_element(By.XPATH, "/html/body/div[4]/div[3]/div/div/div/div/div[2]/div/div/main/div/section/header/h1").text
    return int(connection_count.split(" ")[0].replace(",", ""))

def get_credentials() -> tuple[str, str]:
    """
    Returns the LinkedIn username and password from the .env file
    """
    load_dotenv()
    username = os.getenv("LINKEDIN_USERNAME")
    password = os.getenv("LINKEDIN_PASSWORD")
    return username, password

def connect_to_db() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    """
    Connects to the SQLite database and returns the connection and cursor
    """
    conn = sqlite3.connect('linkedin.db')
    c = conn.cursor()
    
    # Create connections table if it doesn't exist with the following columns: date, connection_count
    c.execute('''CREATE TABLE IF NOT EXISTS connections
                 (date text, connection_count integer)''')

    return conn, c

def clear_db():
    """
    Clears the connections table
    """
    conn, c = connect_to_db()
    c.execute("DROP TABLE connections")
    conn.commit()

def get_connection_data_from_db(c: sqlite3.Cursor) -> list[tuple[str, int]]:
    """
    Returns all the data in the connections table
    """
    c.execute("SELECT * FROM connections")
    return c.fetchall()

def add_connection_data_to_db(c: sqlite3.Cursor, connection_count: int) -> None:
    """
    Adds a row to the connections table
    """
    # Get the date
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    c.execute("INSERT INTO connections VALUES (?, ?)", (today, connection_count))

def plot_connection_data(snapshot: list[tuple[str, int]]) -> None:
    """
    Plots the connection data
    """
    dates = [row[0] for row in snapshot]
    connection_counts = [row[1] for row in snapshot]

    plt.plot(dates, connection_counts)
    plt.xlabel("Date")
    plt.ylabel("Connection Count")
    plt.title("LinkedIn Connection Count Over Time")
    plt.show()

    # Save as .png to the current directory
    plt.savefig("connection_count.png")

def main():
    username, password = get_credentials()
    
    # Make a Chrome driver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    connection_count = get_connection_count(driver, username, password)
    print(f"Connection count: {connection_count}")

    # Get the HTML
    html = driver.page_source 

    # Close the driver
    driver.close()

    conn, c = connect_to_db()

    # Add the connection count to the database
    add_connection_data_to_db(c, connection_count)

    # Select all from the connections table
    snapshot = get_connection_data_from_db(c)
    print(snapshot)

    conn.commit()

    # Plot the connection data
    plot_connection_data(snapshot)

if __name__ == "__main__":
    main()