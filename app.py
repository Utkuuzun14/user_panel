from optparse import Values
from flask import Flask, request, render_template, jsonify, send_file, abort, json
from datetime import date, datetime
import matplotlib as plt
import numpy as np
import glob
from io import BytesIO
from zipfile import ZipFile
import os
import plotly
import plotly.graph_objs as go


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

@app.route('/real-time-row')
def real_time_row():
    return render_template('realtimedata/rowdata.html')

@app.route('/real-time-frequency')
def real_time_frequency():
    return render_template('realtimedata/frequency.html')



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


# TXT DOSYALARINI HTML SAYFASINA AKTAR 
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

    return render_template("records/continuousrec.html", records=records)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

@app.route("/trigger-records")
def trigger_records():
    # trigger_records klasörü içindeki tüm .txt dosyalarını bul
    trigger_folder = os.path.join(BASE_DIR, "trigger_records")
    files = glob.glob(os.path.join(trigger_folder, "*.txt"))
    files.sort(key=os.path.getctime, reverse=True)

    records = []
    for i, file in enumerate(files):
        records.append({
            "id": i,
            "filename": os.path.basename(file),
            "date": datetime.fromtimestamp(os.path.getctime(file)).strftime("%Y-%m-%d %H:%M:%S"),
            "size": f"{round(os.path.getsize(file)/1024, 2)} KB"
        })

    # triggerrec.html dosyası templates/records/ altında
    return render_template("records/triggerrec.html", records=records)




# DOSYA SİLME (Time_Records klasöründe dosya silme)
@app.route("/delete-time-records", methods=["POST"])
def delete_time_records():
    data = request.get_json()
    ids = data.get("ids", [])

    time_dir = os.path.join(os.getcwd(), "time_records")
    all_files = sorted([f for f in os.listdir(time_dir) if f.endswith(".txt")])
    deleted_files = []

    for id in ids:
        try:
            file_index = int(id) - 1
            if 0 <= file_index < len(all_files):
                file_path = os.path.join(time_dir, all_files[file_index])
                os.remove(file_path)
                deleted_files.append(all_files[file_index])
        except Exception as e:
            print(f"Dosya silme hatası: {e}")
    
    return jsonify({"deleted": deleted_files, "message": "Time dosyalar silindi."})


    
# DOSYA SİLME (TRİGGER KAYITLARI İÇİN)
@app.route("/delete-trigger-records", methods=["POST"])
def delete_trigger_records():
    data = request.get_json()
    ids = data.get("ids", [])

    trigger_dir = os.path.join(os.getcwd(), "trigger_records")
    all_files = sorted([f for f in os.listdir(trigger_dir) if f.endswith(".txt")])
    deleted_files = []

    for id in ids:
        try:
            file_index = int(id) - 1
            if 0 <= file_index < len(all_files):
                file_path = os.path.join(trigger_dir, all_files[file_index])
                os.remove(file_path)
                deleted_files.append(all_files[file_index])
        except Exception as e:
            print(f"Dosya silme hatası: {e}")
    
    return jsonify({"deleted": deleted_files, "message": "Trigger dosyalar silindi."})



#Dosya İndirme(TRİGGER KAYITLARI İÇİN)
@app.route('/download-trigger-records', methods=['POST'])
def download_trigger_records():
    data = request.get_json()
    ids = data.get("ids", [])
    trigger_dir = os.path.join(os.getcwd(), "trigger_records")

    all_files = sorted([f for f in os.listdir(trigger_dir) if f.endswith(".txt")])
    selected_files = [
        os.path.join(trigger_dir, all_files[int(id)-1])
        for id in ids if int(id)-1 < len(all_files)
    ]

    if not selected_files:
        return "Dosya bulunamadi", 404

    if len(selected_files) == 1:
        return send_file(selected_files[0], as_attachment=True)

    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zipf:
        for file_path in selected_files:
            zipf.write(file_path, arcname=os.path.basename(file_path))
    zip_buffer.seek(0)

    return send_file(zip_buffer, as_attachment=True, download_name="trigger_kayitlar.zip")


#Dosya İndirme(TIME KAYITLARI İÇİN)
@app.route('/download-time-records', methods=['POST'])
def download_time_records():
    data = request.get_json()
    ids = data.get("ids", [])
    time_dir = os.path.join(os.getcwd(), "time_records")

    all_files = sorted([f for f in os.listdir(time_dir) if f.endswith(".txt")])
    selected_files = [
        os.path.join(time_dir, all_files[int(id)-1])
        for id in ids if int(id)-1 < len(all_files)
    ]

    if not selected_files:
        return "Dosya bulunamadi", 404

    if len(selected_files) == 1:
        return send_file(selected_files[0], as_attachment=True)

    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zipf:
        for file_path in selected_files:
            zipf.write(file_path, arcname=os.path.basename(file_path))
    zip_buffer.seek(0)

    return send_file(zip_buffer, as_attachment=True, download_name="time_kayitlar.zip")


# SAHTE VERİ ÜRETİCİ
def get_machine_data(index):
    return f"TEST_DATA_for_index_{index}"

@app.route('/rowdata')
def rowdata():
    return render_template('realtimedata/rowdata.html')

@app.route('/rowdata/data')
def rowdata_data():
    json_path = os.path.join('static', 'ivme.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    
    sensor_list = raw.get("sensor", [])

    traces = []

    for axis in sensor_list:
        name = axis.get("name")
        waveform = axis.get("waveform", {})
        y_data = waveform.get("wf_values", [])
        dt = waveform.get("dt", 1)
        
        # X ekseni için zaman hesapla
        x_data = [i * dt for i in range(len(y_data))]

        trace = {
            'x': x_data,
            'y': y_data,
            'type': 'scatter',
            'mode': 'lines',
            'name': name
        }

        traces.append(trace)

@app.route('/frequency')
def frequency():
    return render_template('realtimedata/frequency.html')

@app.route('/frequency/data')
def frequency_data():
    json_path = os.path.join('static', 'ivme.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        
        traces = []
        sensor_list = raw.get("sensor", [])
        
        if not sensor_list:  # Sensör listesi boşsa
            return jsonify({"error": "No sensor data found"}), 404
        
        for sensor in sensor_list:
            name = sensor.get("name")
            unit = sensor.get("unit", "")  # Birim bilgisini de ekledik
            waveform = sensor.get("waveform", {})
            values = waveform.get("wf_values", [])
            dt = waveform.get("dt", 1)
            
            # X ve Y değerlerini hesapla
            x = [i * dt for i in range(len(values))]
            y = values
            
            trace = {
                'x': x,
                'y': y,
                'type': 'scatter',
                'mode': 'lines',
                'name': f"{name} ({unit})",  # Birim bilgisini isme ekledik
                'line': {'width': 1.5}  # Çizgi kalınlığı eklendi
            }
            traces.append(trace)
        
        return jsonify({
            "data": traces,
            "layout": {  # Layout bilgisini de ekleyebiliriz
                "title": "Sensör Verileri",
                "xaxis": {"title": "Zaman (s)"},
                "yaxis": {"title": "Genlik"}
            }
        })
    
    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":  
    app.run(debug=True)
