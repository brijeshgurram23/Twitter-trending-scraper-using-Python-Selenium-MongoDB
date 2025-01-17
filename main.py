import time
import json
from datetime import datetime
from webbrowser import BackgroundBrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
from pymongo import MongoClient
import requests
from selenium import *
from flask import Flask, render_template, jsonify
import threading
from dotenv import load_dotenv
import os
load_dotenv()  # Load environment variables from .env file


# PROXYMESH_URL = "http://Brijesh23:michaeljordan23@us-ca.proxymesh.com:31280"

# client = MongoClient('mongodb://localhost:27017/')
MONGO_URL = os.environ.get("MONGO_URL")
client = MongoClient(MONGO_URL)

db = client['twitter_trends']
collection = db['trending_topics']

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument(f'--proxy-server={PROXYMESH_URL}')
    options.headless = False
    driver = webdriver.Chrome(options=options)
    return driver

def login_to_twitter(driver, username, password):
    driver.get("https://twitter.com/login")
    time.sleep(5)

    wait = WebDriverWait(driver, 10)
    
    username_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='username']")))
    
    username_input.send_keys(username)
    username_input.send_keys(Keys.RETURN)
    
    time.sleep(2) 

    # email_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='on']")))
    # email_input.send_keys(email)
    # email_input.send_keys(Keys.RETURN)

    # time.sleep(2)
    password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='current-password']")))
    
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(2)

def click_explore_button(driver):
    try:
        not_now_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Not now']"))
        )
        not_now_button.click()
        
        
    except TimeoutException:
        pass  
    
def get_trending_topics(driver):
     
    time.sleep(2)
  
    
    trends = []
    xpaths = [
        '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/section/div/div/div[4]/div/div/div/div[2]',
        '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/section/div/div/div[5]/div/div/div/div[2]',
        '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/section/div/div/div[6]/div/div/div/div[2]',
        '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/section/div/div/div[7]/div/div/div/div[2]',
        '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/section/div/div/div[8]/div/div/div/div[2]'
]

    for xpath in xpaths:
        try:
           element = driver.find_element(By.XPATH, xpath)
           trends.append(element.text)
        except NoSuchElementException as e:
           print(f"Error finding element for XPath {xpath}: {e}")

    return trends

def save_to_mongodb(trends, ip):
    unique_id = str(datetime.now().timestamp())
    data = {
        "_id": unique_id,
        "trend1": trends[0] if trends else None,
        "trend2": trends[1] if len(trends) > 1 else None,
        "trend3": trends[2] if len(trends) > 2 else None,
        "trend4": trends[3] if len(trends) > 3 else None,
        "trend5": trends[4] if len(trends) > 4 else None,
        "date": datetime.now(),
        "ip_address": ip
    }
    collection.insert_one(data)
    return data


def main(username, password):
    app.logger.info("Initializing WebDriver.")
    driver = get_driver()
    try:
        app.logger.info("Logging into Twitter.")
        login_to_twitter(driver, username, password)

        app.logger.info("Navigating to explore section.")
        click_explore_button(driver)

        app.logger.info("Fetching trending topics.")
        trends = get_trending_topics(driver)

        app.logger.info("Getting IP address.")
        ip = requests.get('https://api.ipify.org').text

        app.logger.info("Saving trends to MongoDB.")
        result = save_to_mongodb(trends, ip)

        app.logger.info(f"Process completed. Result: {result}")
    except Exception as e:
        app.logger.error(f"Error in main function: {e}", exc_info=True)
        raise
    finally:
        driver.quit()
    return result






app = Flask(__name__,template_folder='templates')


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run-script")
def run_script():
    TWITTER_USERNAME = os.environ.get("TWITTER_USERNAME")
    TWITTER_PASSWORD = os.environ.get("TWITTER_PASSWORD")
    try:
        app.logger.info("Starting the main script.")
        result = main(TWITTER_USERNAME, TWITTER_PASSWORD)
        app.logger.info(f"Script completed successfully. Result: {result}")
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error in /run-script: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
