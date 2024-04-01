import datetime, time, re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, url):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Headless 모드 활성화
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
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
        match = re.match(r'(.+)\((.+)\)', self.subject)
        if match:
            self.subject1 = match.group(1).strip()  # 괄호 앞의 내용
            self.subject2 = match.group(2).strip()  # 괄호 안의 내용
        else:
            print("No match found.")
        
        bible_text = soup.find("p", id="qt_bible")
        for text in bible_text.find_all("p"):
            self.contents.append(text.get_text(strip=True) + "\n")  # 각 문장 끝에 공백 추가
        
        for line in self.contents:
            match = re.match(r'(\d+)(.+)', line)
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

    print("Date: ", datetime.date.today())
    print("Subject:", qt_scraper.subject1)
    print("Verse:", qt_scraper.subject2)
    print("Contents:\n", qt_scraper.contents)

    print("Separated:\n", qt_scraper.separated_contents)
    print("number", qt_scraper.number)
    print("text", qt_scraper.text)
