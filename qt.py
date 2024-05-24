import datetime, time, re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import json
import secret_keys

cred = credentials.Certificate(
    "/Users/slave4jx/Documents/secrets/cbranding-app-firebase-adminsdk-hqzje-7b6fc40196.json"
)
firebase_admin.initialize_app(cred)
db = firestore.client()  # Firestore 클라이언트 인스턴스 생성


class Scraper:
    def __init__(self, url):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless=new")  # Headless 모드 활성화
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(service=Service(), options=self.chrome_options)
        self.url = url

    def scrap(self):
        self.driver.get(self.url)
        time.sleep(3)  # 페이지 로딩 대기
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        return soup


class QT(Scraper):
    def __init__(self, url, api_key):
        super().__init__(url)
        self.api_key = api_key  # API 키 저장
        self.subject = ""
        self.subject1 = ""
        self.subject2 = ""
        self.contents = []
        self.number = ""
        self.text = ""
        self.separated_contents = []

    def get_content(self):
        soup = self.scrap()
        self.subject = soup.find("h2", class_="qt_subject").get_text(strip=True)
        match = re.match(r"(.+)\((.+)\)", self.subject)
        if match:
            self.subject1 = match.group(1).strip()
            self.subject2 = match.group(2).strip()
        else:
            print("No match found.")

        bible_text = soup.find("p", id="qt_bible")
        for text in bible_text.find_all("p"):
            self.contents.append(text.get_text(strip=True) + "\n")

        for line in self.contents:
            match = re.match(r"(\d+)(.+)", line)
            if match:
                self.number = match.group(1)
                self.text = match.group(2)
                self.separated_contents.append((self.number, self.text))
            else:
                print(f"No match found for line: {line}")

    def fetch_latest_video_id(self, channel_id):
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=1&order=date&type=video&key={self.api_key}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = json.loads(response.text)
                if data["items"]:
                    return data["items"][0]["id"]["videoId"]
                return None
            else:
                print("Failed to load video")
                print(f"Status code: {response.status_code}")
                print(f"Response body: {response.text}")
                return None
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None


if __name__ == "__main__":
    url = "http://app.kccc.org/soonjang/?p=spirit/qt"
    api_key = secret_keys.YOUTUBE_API_KEY
    qt_scraper = QT(url, api_key)
    qt_scraper.get_content()

    channel_id = "UC7ueCtbLRAmctB0uv3MxAnQ"
    latest_video_id = qt_scraper.fetch_latest_video_id(channel_id)

    # 배열을 딕셔너리 리스트로 변환
    contents_dicts = [
        {"number": item[0], "text": item[1]} for item in qt_scraper.separated_contents
    ]
    data = {
        "date": datetime.date.today().isoformat(),
        "subject1": qt_scraper.subject1,
        "subject2": qt_scraper.subject2,
        "contents": contents_dicts,
        "videoId": latest_video_id if latest_video_id else "No video available",
    }

    # Firebase에 데이터 업로드
    doc_ref = db.collection("qt-data").document(data["date"])
    doc_ref.set(data)
    print("Data uploaded to Firebase with structured format.")
    print("Date: ", datetime.date.today())
    print("Subject:", qt_scraper.subject1)
    print("Verse:", qt_scraper.subject2)
    print("Contents:\n", qt_scraper.contents)
    print("Separated:\n", qt_scraper.separated_contents)
    print("number", qt_scraper.number)
    print("text", qt_scraper.text)
    print("videoId", latest_video_id)
