import os, pytz
from datetime import datetime
from flask import Flask, render_template
from qt import QT

app = Flask("QT")

@app.route("/")
def index():
  # url = "http://app.kccc.org/soonjang/?p=spirit/qt"
  # qt = QT(url)
  # qt.get_content()
  # korea_tz = pytz.timezone('Asia/Seoul')
  # now_in_korea = datetime.now(korea_tz)
  # today = now_in_korea.date()
  # return render_template("index.html", subject1=qt.subject1, subject2=qt.subject2, contents=qt.separated_contents, today=today)
    return render_template("index.html")

if __name__ == "__main__":
    # 환경 변수에서 PORT 값을 가져옵니다. 설정되어 있지 않은 경우, 기본값으로 8080을 사용합니다.
    port = int(os.getenv('PORT', 8000))
    # host='0.0.0.0'은 애플리케이션이 모든 네트워크 인터페이스에서 접근 가능하도록 설정합니다.
    app.run(host='0.0.0.0', port=port, debug=True)
