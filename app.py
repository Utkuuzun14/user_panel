from flask import Flask, request, render_template, redirect, url_for , jsonify
from datetime import datetime
import os
import random

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/')
def index():
    return render_template('/settings/recordset.html')

@app.route("/start_recording", methods=["POST"]) 
def start_recording():
    # Formdan verileri alıyoruz
    active_flags = request.form.getlist("active[]")
    start_times = request.form.getlist("startTime[]")  # form input name ile birebir eşleşmeli
    end_times = request.form.getlist("endTime[]")
    durations = request.form.getlist("duration[]")
    units = request.form.getlist("unit[]")
    
    # "active[]" checkbox'ları formda 'on' olarak geliyor, işaretli olanların indexlerini alıyoruz
    active_indices = [i for i, val in enumerate(active_flags) if val == 'on']
    array_size = len(active_indices)

    output_lines = []
    output_lines.append(f"arraysize: {array_size}\n")

    for new_index, original_index in enumerate(active_indices):
        start = start_times[original_index]
        end = end_times[original_index]
        dura = durations[original_index]
        unit = units[original_index]

        test_data = get_machine_data(new_index)

        output_lines.append(f"[{new_index}] start: {start}, end: {end}, duration: {duration}, unit: {unit}, data: {test_data}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"time_records_{timestamp}.txt"

    with open(filename, 'w') as file:
        file.write("\n".join(output_lines))

    return jsonify({"message": f"{filename} dosyasına kaydedildi."})

def get_machine_data(index):
    # Gerçek makineden veri gelene kadar test verisi döndür
    return f"TEST_DATA_for_index_{index}"

if __name__ == "__main__":
    app.run(debug=True)
