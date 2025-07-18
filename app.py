from flask import Flask, render_template, request, redirect, url_for
from flask_apscheduler import APScheduler
from datetime import datetime

app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Ana Sayfa (istersen yönlendirilebilir)
@app.route("/")
def index():
    return redirect(url_for("settings_record"))

# SettingsRecord Sayfası
@app.route("/settingsRecord")
def settings_record():
    return render_template("settings/recordset.html")

@app.route("/startRecording", methods=["POST"])
def start_recording():
    interval = request.form.get("recordPeriod")
    start_times = request.form.getlist("startTime[]")
    end_times = request.form.getlist("endTime[]")
    frequencies = request.form.getlist("frequency[]")
    units = request.form.getlist("unit[]")
    actives = request.form.getlist("active[]")

    print("recordPeriod:", interval)
    print("startTimes:", start_times)
    print("endTimes:", end_times)
    print("frequencies:", frequencies)
    print("units:", units)
    print("actives:", actives)

    return redirect(url_for("settings_record"))


# Kayıt Alınan Fonksiyon (Terminal + Dosyaya kayıt)
def record_data():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Kayıt alındı: {now}")
    with open("records.txt", "a") as f:
        f.write(f"{now}\n")

# # Kayıtları Gösteren Sayfa (opsiyonel)
# @app.route("/recordLogs")
# def show_logs():
#     try:
#         with open("records.txt", "r") as f:
#             lines = f.readlines()[-30:]  # Son 30 kayıt
#     except FileNotFoundError:
#         lines = []
#     return render_template("record_logs.html", logs=lines)

if __name__ == "__main__":
    app.run(debug=True,port="5500")
