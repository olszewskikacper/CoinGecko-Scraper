import requests
from bs4 import BeautifulSoup
import pandas as pd
from playwright.sync_api import sync_playwright
from time import sleep
import random
import csv
import os
from tkinter import filedialog
from tkinter import *
import shutil
from flask import flash
import mysql.connector

db_config = {
    'user': 'root',
    'password': 'admin',
    'host': 'localhost',
    'database': 'usersdb'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def clean_text(text):
    """ Utility function to clean text by removing extra spaces and newlines. """
    if text:
        return ' '.join(text.split())
    return 'N/A'

def insert_data_to_db(data):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        delete_query = "DELETE FROM crypto_data"
        cursor.execute(delete_query)

        insert_query = """
        INSERT INTO crypto_data (
            name, price, change_1h, direction_1h, change_24h, direction_24h,
            change_7d, direction_7d, change_30d, direction_30d, volume_24h,
            circulating_supply, total_supply
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for entry in data:
            cursor.execute(insert_query, (
                entry['Name'], entry['Price'], entry['Change 1h'], entry['Direction 1h'],
                entry['Change 24h'], entry['Direction 24h'], entry['Change 7d'], entry['Direction 7d'],
                entry['Change 30d'], entry['Direction 30d'], entry['24h Volume'],
                entry['Circulating Supply'], entry['Total Supply']
            ))

        connection.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def scrape_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.coingecko.com/en/all-cryptocurrencies")
        print(page.title())
        for _ in range(1, 6):
            selector = '[data-action="click->more-content#loadMoreContent"][data-more-content-target="loadMoreButton"]'
            page.click(selector)
            sleep(0.5)
        kontent = page.content()
        browser.close()

    data = []
    soup = BeautifulSoup(kontent, 'html.parser')
    rows = soup.select('table tbody tr[data-view-component="true"]')
    print(f"Number of rows found: {len(rows)}")
    for row in soup.select('table tbody tr[data-view-component="true"]'):
        name_element = row.select_one('.tw-text-gray-700.tw-font-semibold')
        name = clean_text(name_element.text) if name_element else 'N/A'

        price_element = row.select_one('[data-price-target="price"]')
        price = clean_text(price_element.text) if price_element else 'N/A'

        def get_change_and_direction(td_index):
            change_element = row.select_one(f'td:nth-of-type({td_index}) .gecko-down, td:nth-of-type({td_index}) .gecko-up')
            if change_element:
                change = clean_text(change_element.text)
                direction = 'down' if 'gecko-down' in change_element.get('class', []) else 'up'
            else:
                change = 'N/A'
                direction = 'N/A'
            return change, direction

        change_1h, direction_1h = get_change_and_direction(4)
        change_24h, direction_24h = get_change_and_direction(5)
        change_7d, direction_7d = get_change_and_direction(6)
        change_30d, direction_30d = get_change_and_direction(7)

        volume_24h_element = row.select_one('td:nth-of-type(8)')
        volume_24h = clean_text(volume_24h_element.text) if volume_24h_element else 'N/A'

        circulating_supply_element = row.select_one('td:nth-of-type(9)')
        circulating_supply = clean_text(circulating_supply_element.text) if circulating_supply_element else 'N/A'

        total_supply_element = row.select_one('td:nth-of-type(10)')
        total_supply = clean_text(total_supply_element.text) if total_supply_element else 'N/A'

        data.append({
            'Name': name,
            'Price': price,
            'Change 1h': change_1h,
            'Direction 1h': direction_1h,
            'Change 24h': change_24h,
            'Direction 24h': direction_24h,
            'Change 7d': change_7d,
            'Direction 7d': direction_7d,
            'Change 30d': change_30d,
            'Direction 30d': direction_30d,
            '24h Volume': volume_24h,
            'Circulating Supply': circulating_supply,
            'Total Supply': total_supply
        })

    if data:
        insert_data_to_db(data)
        print("Data has been inserted into the database.")
    else:
        print("No data to insert into the database.")

 

def get_random_crypto():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM crypto_data")
        rows = cursor.fetchall()

        if not rows:
            print("Error: No data available in the database.")
            return None

        random_row = random.choice(rows)
        return random_row

    except mysql.connector.Error as err:
        print(f"Error: Failed to retrieve data from the database due to the following error: {err}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
def download_csv_to_folder(directory=None):
    root = Tk()
    root.withdraw()

    if directory is None:
        folder_selected = filedialog.askdirectory()
    else:
        folder_selected = directory

    

    try:
        if os.path.exists("Crypto Data.csv"):
            destination_file_path = os.path.join(folder_selected, "Crypto Data.csv")

            shutil.copyfile("Crypto Data.csv", destination_file_path)
            print(f"File 'Crypto Data.csv' downloaded to: {destination_file_path}")
        else:
            print(f"Error: Source file '{"Crypto Data.csv"}' not found.")
    except Exception as e:
        print(f"Error occurred: {e}")


def read_users():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT username, password FROM users")
        users = cursor.fetchall()
        return users
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def write_user(user):
    users = read_users()
    if user['username'] not in [u['username'] for u in users]:
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                           (user['username'], user['password']))
            connection.commit()
            flash('Account created successfully!', category='success')
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('Failed to create account. Please try again.', category='error')
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        flash('Username already exists. Please choose a different username.', category='error')


