import os
import pytz
import datetime
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

class QT:
    def __init__(self):
        self.url = "http://app.kccc.org/soonjang/?p=spirit/qt"

    def get_cached_data(self):
        cached_data = self.retrieve_cached_data()
        if not cached_data or self.is_cache_expired(cached_data['date']):
            new_data = self.scrape_data()
            self.cache_data(new_data)
            return new_data
        else:
            return cached_data['data']

    def retrieve_cached_data(self):
        try:
            with open('cached_data.txt', 'r') as file:
                cached_data = eval(file.read())
                return cached_data
        except FileNotFoundError:
            return None

    def is_cache_expired(self, cached_date):
        today = datetime.date.today()
        return cached_date != today

    def scrape_data(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=Service(), options=chrome_options)
        
        driver.get(self.url)
        time.sleep(3)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        
        subject = soup.find("h2", class_="qt_subject").get_text(strip=True)
        match = re.match(r'(.+)\((.+)\)', subject)
        if match:
            subject1 = match.group(1).strip()
            subject2 = match.group(2).strip()
        else:
            subject1 = "No match found"
            subject2 = "No match found"
        
        contents = []
        bible_text = soup.find("p", id="qt_bible")
        for text in bible_text.find_all("p"):
            contents.append(text.get_text(strip=True) + "\n")
        
        separated_contents = []
        for line in contents:
            match = re.match(r'(\d+)(.+)', line)
            if match:
                number = match.group(1)
                text = match.group(2)
                separated_contents.append((number, text))
        
        data = {
            "date": datetime.date.today(),
            "data": {
                "subject1": subject1,
                "subject2": subject2,
                "contents": separated_contents
            }
        }
        
        driver.quit()
        return data

    def cache_data(self, data):
        with open('cached_data.txt', 'w') as file:
            file.write(str(data))

if __name__ == "__main__":
    qt = QT()
    cached_data = qt.get_cached_data()
    print(cached_data)
