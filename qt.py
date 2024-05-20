import datetime, time, re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
import json

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
        # Chrome 드라이버 인스턴스 생성 시, ChromeOptions 사용
        self.driver = webdriver.Chrome(service=Service(), options=self.chrome_options)

        self.url = url

    def scrap(self):
        self.driver.get(self.url)
        time.sleep(3)  # 페이지 로딩 대기
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        return soup


class QT(Scraper):
    def __init__(self, url):
        super().__init__(url)
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
            self.subject1 = match.group(1).strip()  # 괄호 앞의 내용
            self.subject2 = match.group(2).strip()  # 괄호 안의 내용
        else:
            print("No match found.")

        bible_text = soup.find("p", id="qt_bible")
        for text in bible_text.find_all("p"):
            self.contents.append(
                text.get_text(strip=True) + "\n"
            )  # 각 문장 끝에 공백 추가

        for line in self.contents:
            match = re.match(r"(\d+)(.+)", line)
            if match:
                self.number = match.group(1)
                self.text = match.group(2)
                self.separated_contents.append((self.number, self.text))
            else:
                print(f"No match found for line: {line}")


if __name__ == "__main__":
    url = "http://app.kccc.org/soonjang/?p=spirit/qt"
    qt_scraper = QT(url)
    qt_scraper.get_content()

    # 배열을 딕셔너리 리스트로 변환
    contents_dicts = [
        {"number": item[0], "text": item[1]} for item in qt_scraper.separated_contents
    ]

    data = {
        "date": datetime.date.today().isoformat(),
        "subject1": qt_scraper.subject1,
        "subject2": qt_scraper.subject2,
        "contents": contents_dicts,  # JSON 변환 대신 딕셔너리 리스트 사용
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
