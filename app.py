from flask import Flask, request, render_template, jsonify, send_file, abort
from datetime import datetime
import os
import glob
from io import BytesIO
from zipfile import ZipFile

app = Flask(__name__)

# KAYITLARIN TUTULACAĞI KLASÖR
RECORDS_FOLDER = os.path.join(os.path.dirname(__file__), "time_records")
os.makedirs(RECORDS_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trigger_settings')
def trigger_settings():
    # trigger_settings.html dosyan var mı? Yoksa placeholder da olabilir.
    return render_template('settings/triggerset.html')

@app.route('/network_settings')
def network_settings():
    return render_template('settings/networkset.html')

@app.route('/record_settings')
def record_settings():
    return render_template('settings/recordset.html')

@app.route('/advanced_settings')
def advanced_settings():
    return render_template('advancedset.html')

@app.route('/trigger_records')
def trigger_records():
    # Burada kayıtları gösteren sayfa için işlem yapabilirsin
    return render_template('triggerrec.html')



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

# TXT DOSYALARINI AL (JSON API)
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

# TXT DOSYALARINI HTML SAYFASINA AKTAR (YENİ!)
@app.route("/records")
def records_page():
    files = glob.glob(os.path.join(RECORDS_FOLDER, "*.txt"))
    files.sort(key=os.path.getctime, reverse=True)

    records = []
    for i, file in enumerate(files):
        records.append({
            "id": i,
            "filename": os.path.basename(file),
            "date": datetime.fromtimestamp(os.path.getctime(file)).strftime("%Y-%m-%d %H:%M:%S"),
            "size": f"{round(os.path.getsize(file)/1024, 2)} KB"
        })

    return render_template("records/continiousrec.html", records=records)

# TXT DOSYASI İÇERİĞİNİ HTML SAYFADA GÖSTER (YENİ ROUTE)
@app.route("/record/<filename>")
def record_content_page(filename):
    # Dosya adı güvenlik için kontrol edilebilir
    if ".." in filename or filename.startswith("/"):
        abort(400, "Geçersiz dosya adı")

    filepath = os.path.join(RECORDS_FOLDER, filename)
    if not os.path.exists(filepath):
        abort(404, "Dosya bulunamadı")

    with open(filepath, 'r', encoding="utf-8") as f:
        content = f.read()

    return render_template("records/record_content.html", filename=filename, content=content)

# DOSYA İÇERİĞİNİ JSON OLARAK DÖNEN API (İstersen kullanabilirsin)
# @app.route("/api/record_content")
# def get_record_content():
#     filename = request.args.get("filename")
#     if not filename:
#         return jsonify({"error": "Dosya adı belirtilmeli"}), 400

#     filepath = os.path.join(RECORDS_FOLDER, filename)
#     if not os.path.exists(filepath):
#         return jsonify({"error": "Dosya bulunamadı"}), 404

#     with open(filepath, 'r', encoding="utf-8") as f:
#         content = f.read()
    
#     return jsonify({
#         "filename": filename,
#         "content": content
#     })

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

# SAHTE VERİ ÜRETİCİ
def get_machine_data(index):
    return f"TEST_DATA_for_index_{index}"

#Dosya İndirme
@app.route('/download-records', methods=['POST'])
def download_records():
    data = request.get_json()
    ids = data.get("ids", [])

    # time_records klasöründen tüm txt dosyalarını sırayla al
    all_files = sorted(
        [f for f in os.listdir(RECORDS_DIR) if f.endswith(".txt")]
    )

    # ID'ler sırasına göre eşleştir (1-based index)
    selected_files = [
        os.path.join(RECORDS_DIR, all_files[int(id)-1])
        for id in ids if int(id)-1 < len(all_files)
    ]

    if not selected_files:
        return "Dosya bulunamadı", 404

    if len(selected_files) == 1:
        return send_file(selected_files[0], as_attachment=True)

    # Çoklu dosya: ziple
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zipf:
        for file_path in selected_files:
            zipf.write(file_path, arcname=os.path.basename(file_path))
    zip_buffer.seek(0)

    return send_file(zip_buffer, as_attachment=True, download_name="kayitlar.zip")

if __name__ == "__main__":  
    app.run(debug=True)
