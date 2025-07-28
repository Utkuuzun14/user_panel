from flask import Flask, request, render_template, jsonify, send_file
from datetime import datetime
import os
import glob

app = Flask(__name__)

# KAYITLARIN TUTULACAĞI KLASÖR
RECORDS_FOLDER = "time_records"
os.makedirs(RECORDS_FOLDER, exist_ok=True)

# ANA SAYFA
@app.route('/')
def index():
    return render_template('settings/recordset.html')

# KAYIT BAŞLATMA
@app.route("/start_recording", methods=["POST"])
def start_recording():
    active_flags = request.form.getlist("active[]")
    start_times = request.form.getlist("startTime[]")
    end_times = request.form.getlist("endTime[]")
    durations = request.form.getlist("duration[]")
    units = request.form.getlist("unit[]")

    active_indices = [i for i, val in enumerate(active_flags) if val == 'on']
    array_size = len(active_indices)

    output_lines = [f"arraysize: {array_size}"]

    for new_index, original_index in enumerate(active_indices):
        output_lines.append(
            f"[time_based_record_{new_index}] start: {start_times[original_index]}, "
            f"end: {end_times[original_index]}, duration: {durations[original_index]}, "
            f"unit: {units[original_index]}, data: {get_machine_data(new_index)}"
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"time_records_{timestamp}.txt"
    filepath = os.path.join(RECORDS_FOLDER, filename)

    with open(filepath, 'w') as file:
        file.write("\n".join(output_lines))

    return jsonify({
        "success": True,
        "message": "Kayıt başarıyla oluşturuldu",
        "filename": filename
    })

# KAYITLARI LİSTELEME (JSON API)
@app.route("/api/records")
def get_records():
    files = glob.glob(os.path.join(RECORDS_FOLDER, "*.txt"))
    files.sort(key=os.path.getctime, reverse=True)

    records = []
    for file in files:
        records.append({
            "filename": os.path.basename(file),
            "date": datetime.fromtimestamp(os.path.getctime(file)).strftime("%Y-%m-%d %H:%M:%S"),
            "size": f"{round(os.path.getsize(file)/1024, 2)} KB",
            "path": file
        })
    
    return jsonify(records)

# KAYIT İÇERİĞİNİ GÖSTERME
@app.route("/api/record_content")
def get_record_content():
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "Dosya adı belirtilmeli"}), 400

    filepath = os.path.join(RECORDS_FOLDER, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Dosya bulunamadı"}), 404

    with open(filepath, 'r') as f:
        content = f.read()
    
    return jsonify({
        "filename": filename,
        "content": content
    })

# DOSYA İNDİRME
@app.route("/download")
def download_file():
    filename = request.args.get("filename")
    if not filename:
        return "Dosya adı belirtilmeli", 400

    filepath = os.path.join(RECORDS_FOLDER, filename)
    if not os.path.exists(filepath):
        return "Dosya bulunamadı", 404

    return send_file(filepath, as_attachment=True)

# DOSYA SİLME
@app.route("/delete", methods=["DELETE"])
def delete_file():
    filename = request.json.get("filename")
    if not filename:
        return jsonify({"error": "Dosya adı belirtilmeli"}), 400

    filepath = os.path.join(RECORDS_FOLDER, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Dosya bulunamadı"}), 404

    os.remove(filepath)
    return jsonify({"success": True})

# TEST VERİSİ ÜRETİCİ
def get_machine_data(index):
    return f"TEST_DATA_for_index_{index}"

# KAYITLAR SAYFASI
@app.route("/records")
def records_page():
    return render_template("records/continiousrec.html")

# GELİŞMİŞ AYARLAR SAYFASI
@app.route('/advancedsetting')
def advancedsetting():
    return render_template('advancedset.html')

if __name__ == "__main__":
    app.run(debug=True)