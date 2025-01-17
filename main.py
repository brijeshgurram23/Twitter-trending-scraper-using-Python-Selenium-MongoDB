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


PROXYMESH_URL = "http://Brijesh23:michaeljordan23@open.proxymesh.com:31280"

# client = MongoClient('mongodb://localhost:27017/')
MONGO_URL = 'mongodb+srv://brijeshgurram910:brijeshgurram910@brijesh23.nbus32j.mongodb.net/?retryWrites=true&w=majority&appName=brijesh23'
client = MongoClient(MONGO_URL)

db = client['twitter_trends']
collection = db['trending_topics']

def get_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run Chrome in headless mode (without UI)
    # options.add_argument(f'--proxy-server={PROXYMESH_URL}')
    options.headless = False
    driver = webdriver.Chrome(options=options)
    return driver

def login_to_twitter(driver, username, password):
    driver.get("https://twitter.com/login")
    time.sleep(2)

    wait = WebDriverWait(driver, 20)
    
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
    driver = get_driver()
    try:
        login_to_twitter(driver, username, password)
        click_explore_button(driver)

        trends = get_trending_topics(driver)
        ip = requests.get('https://api.ipify.org').text
        result = save_to_mongodb(trends, ip)
    finally:
        driver.quit()
    return result





app = Flask(__name__,template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script')
def run_script():
    TWITTER_USERNAME = "BrijeshGurram"
    TWITTER_PASSWORD = "michaeljordan23"
    # TWITTER_EMAIL = "brijeshgurram910@gmail.com"

    result = main(TWITTER_USERNAME, TWITTER_PASSWORD)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
