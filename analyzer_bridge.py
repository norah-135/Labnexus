import time
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# طابور البيانات الخام القادمة من منفذ الجهاز
incoming_port_data = []

def serial_port_worker(port_name="COM3", baud_rate=9600):
    """
    الاستماع لمنفذ السيريال الحقيقي لجهاز التحليل وقراءة البيانات الخام
    """
    try:
        import serial
        ser = serial.Serial(port_name, baud_rate, timeout=1)
        print(f"[*] جاري الاستماع للمنفذ {port_name}...")
        while True:
            if ser.in_waiting > 0:
                raw_line = ser.readline().decode('utf-8', errors='ignore').strip()
                if raw_line:
                    # تقسيم البيانات القادمة من الجهاز (Barcode | Raw Analyzer Data)
                    parts = raw_line.split('|')
                    barcode = parts[0].strip()
                    payload = parts[1].strip() if len(parts) > 1 else raw_line
                    incoming_port_data.append({"sample_id": barcode, "raw_dump": payload})
                    print(f"[+] تم استلام قراءة من الجهاز للباركود: {barcode}")
            time.sleep(0.1)
    except Exception as e:
        print(f"[i] تنبيه المنفذ: {e}")

# واجهة سحب البيانات للموقع
@app.route('/api/port-data', methods=['GET'])
def get_port_data():
    global incoming_port_data
    data = list(incoming_port_data)
    incoming_port_data.clear()
    return jsonify({"success": True, "readings": data})

# واجهة لمحاكاة إرسال قراءة من المنفذ بضغطة زر
@app.route('/api/simulate-port-input', methods=['POST'])
def simulate_input():
    req = request.json or {}
    sample_id = req.get("sample_id", "SMP-BRY-801")
    raw_data = req.get("raw_dump", "ANALYZER_DEV_01 >> K+: 4.3 mmol/L | Na+: 139 mmol/L | STATUS: OK | REF: VALIDATED")
    incoming_port_data.append({"sample_id": sample_id, "raw_dump": raw_data})
    return jsonify({"success": True, "message": "تم ضخ القراءة للمنفذ"})

if __name__ == '__main__':
    threading.Thread(target=serial_port_worker, daemon=True).start()
    print("[*] مستمع المنفذ يعمل على: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)