from flask import Flask, request, render_template, jsonify
from datetime import datetime
import os
import glob

app = Flask(__name__)

@app.route('/load_records')
def load_records():
    list_of_files = glob.glob("time_records/*.txt")
    if not list_of_files:
        return jsonify({"error": "No files found"})

    latest_file = max(list_of_files, key=os.path.getctime)

    with open(latest_file, "r") as f:
        lines = f.readlines()

    records = []
    for line in lines:
        if line.startswith("[time_based_record_"):
            record = {}
            header_end = line.find("]") + 1
            header = line[1:header_end - 1]  # örnek: time_based_record_0
            line_data = line[header_end:].strip()
            record["record_id"] = header

            parts = line_data.split(", ")
            for part in parts:
                if ": " in part:
                    key, val = part.split(": ", 1)
                    record[key.strip()] = val.strip()
            records.append(record)

    return jsonify(records)

# Arayüz
@app.route('/')
def index():
    return render_template('/settings/recordset.html')

# Formdan gelen kayıt verilerini işleyip .txt dosyasına yazar
@app.route("/start_recording", methods=["POST"])
def start_recording():
    active_flags = request.form.getlist("active[]")
    start_times = request.form.getlist("startTime[]")
    end_times = request.form.getlist("endTime[]")
    durations = request.form.getlist("duration[]")
    units = request.form.getlist("unit[]")

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

        output_lines.append(
            f"[time_based_record_{new_index}] start: {start}, end: {end}, duration: {dura}, unit: {unit}, data: {test_data}"
        )

    # Klasör yoksa oluştur
    if not os.path.exists("time_records"):
        os.makedirs("time_records")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"time_records/time_records_{timestamp}.txt"

    with open(filename, 'w') as file:
        file.write("\n".join(output_lines))

    return jsonify({"message": f"{filename} dosyasına kaydedildi."})

# Test verisi simülasyonu
def get_machine_data(index):
    return f"TEST_DATA_for_index_{index}"

@app.route('/advancedsetting')
def advancedsetting():
    return render_template('advancedset.html')




if __name__ == "__main__":
    app.run(debug=True)
