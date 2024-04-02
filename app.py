import os, pytz
from datetime import datetime
from flask import Flask, render_template
from qt import QT

app = Flask("QT")

# 캐시를 저장할 전역 변수
cached_data = {
    "date": None,
    "data": None
}

@app.route("/")
def index():
    global cached_data
    korea_tz = pytz.timezone('Asia/Seoul')
    now_in_korea = datetime.now(korea_tz)
    today = now_in_korea.date()

    # 오늘 날짜의 데이터가 캐시되어 있는지, 데이터가 비어있는지 확인
    if cached_data["date"] != today or not cached_data["data"]:
        # 새로운 날짜의 데이터를 크롤링하고 캐시합니다.
        url = "http://app.kccc.org/soonjang/?p=spirit/qt"
        qt = QT(url)
        qt.get_content()

        # 크롤링 결과가 비어있지 않은지 확인
        if qt.subject1 and qt.subject2 and qt.separated_contents:
            cached_data = {
                "date": today,
                "data": {
                    "subject1": qt.subject1,
                    "subject2": qt.subject2,
                    "contents": qt.separated_contents
                }
            }
        else:
            # 크롤링 결과가 비어있으면, 오류 메시지나 기본값 설정 등의 처리를 추가할 수 있습니다.
            print("Crawling failed or returned empty data. Consider retrying or setting default values.")

    # 캐시된 데이터를 사용하여 템플릿 렌더링
    return render_template("index.html", **cached_data["data"], today=today)


if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
