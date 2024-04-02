import os
from flask import Flask, render_template
from qt import QT

app = Flask("QT")

@app.route("/")
def index():
    qt = QT()
    cached_data = qt.get_cached_data()
    return render_template("index.html", **cached_data)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
