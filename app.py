from flask import Flask, render_template, Response, jsonify
import pytz, os, json
from datetime import datetime
from flask_cors import CORS

from qt import QT

import firebase_admin
from firebase_admin import credentials, firestore

app = Flask("QT")
CORS(app)

cached_data = {
    "date": None,
    "subject1": None,
    "subject2": None,
    "contents": None
}

def get_or_update_data():
    global cached_data
    korea_tz = pytz.timezone('Asia/Seoul')
    now_in_korea = datetime.now(korea_tz)
    today = now_in_korea.date()
    weekday = now_in_korea.weekday()

    if weekday == 6:
        return None  # 일요일 데이터가 필요 없는 경우

    if cached_data["date"] != today or not cached_data["subject1"] or not cached_data["subject2"] or not cached_data["contents"]:
        url = "http://app.kccc.org/soonjang/?p=spirit/qt"
        qt = QT(url)
        qt.get_content()

        if qt.subject1 and qt.subject2 and qt.separated_contents:
            cached_data = {
                "date": today,
                "subject1": qt.subject1,
                "subject2": qt.subject2,
                "contents": qt.separated_contents
            }
        else:
            print("Crawling failed or returned empty data. Consider retrying or setting default values.")
            return None  # 데이터 크롤링 실패 처리
    return cached_data

@app.route("/")
def index():
    data = get_or_update_data()
    if data:
        return render_template("index.html", subject1=data["subject1"], subject2=data["subject2"], contents=data["contents"], today=cached_data["date"])
    else:
        return render_template("sunday.html", today=cached_data["date"])

@app.route("/api/data")
def api_data():
    data = get_or_update_data()
    if data:
        # Using json.dumps to ensure unicode characters are properly rendered
        json_data = json.dumps({
            "date": cached_data["date"].isoformat(),
            "subject1": data["subject1"],
            "subject2": data["subject2"],
            "contents": data["contents"]
        }, ensure_ascii=False)
        return Response(json_data, mimetype='application/json', status=200)
    else:
        return jsonify({"error": "No data available"}), 404

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
    
