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
import matplotlib.dates as mdates

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
    
    # Create connections table if it doesn't exist with the following columns: datetime, connection_count
    c.execute('''CREATE TABLE IF NOT EXISTS connections
                 (datetime text, connection_count integer)''')

    return conn, c

def clear_db() -> None:
    """
    Clears the connections table
    """
    conn, c = connect_to_db()
    c.execute("DROP TABLE IF EXISTS connections")
    conn.commit()
    c.execute('''CREATE TABLE IF NOT EXISTS connections
                    (datetime text, connection_count integer)''')
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
    # Get the current datetime
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO connections VALUES (?, ?)", (current_datetime, connection_count))

def plot_connection_data(snapshot: list[tuple[str, int]]) -> None:
    """
    Plots the connection data and saves the plot as a PNG file
    """
    if not snapshot:
        print("No data to plot.")
        return

    datetimes = [datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in snapshot]

    print("Datetimes:", datetimes) # outputs: datetime.datetime(2024, 6, 8, 17, 0, 49)
    print(f"Original Date Data: {snapshot[0][0]}") # outputs: 2024-06-08 17:00:49

    connection_counts = [row[1] for row in snapshot]

    # Print data points to verify
    print("Datetimes:", datetimes)
    print("Connection Counts:", connection_counts)

    plt.figure(figsize=(10, 5))
    plt.plot(datetimes, connection_counts, marker='o')  # Add markers to the plot
    plt.xlabel("Datetime")
    plt.ylabel("Connection Count")
    plt.title("LinkedIn Connection Count Over Time")
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))  # Custom date format
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())  # Automatically adjust the date ticks
    plt.tight_layout()  # Adjust layout to fit datetime labels
    
    # Save as .png to the current directory
    plt.savefig("connection_count.png")

    plt.show()

def push_to_github():
    os.system("git add .")
    os.system("git commit -m 'Update connection count'")
    os.system("git push")

def insert_custom_amount(c: sqlite3.Cursor) -> None:
    amount = int(input("Enter the amount of connections: "))
    add_connection_data_to_db(c, amount)

def main():
    username, password = get_credentials()
    
    # Make a Chrome driver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    connection_count = get_connection_count(driver, username, password)
    print(f"Connection count: {connection_count}")

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

    if input("Push to GitHub? (y/n): ").lower() == "y":
        push_to_github()

if __name__ == "__main__":
    # main()
    # clear_db()

    conn, c = connect_to_db()
    insert_custom_amount(c)

    conn.commit()

    snapshot = get_connection_data_from_db(c)
    plot_connection_data(snapshot)

    conn.close()