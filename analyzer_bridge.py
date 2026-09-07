import json
import time
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# طابور العينات التي تم الانتهاء من فحصها عبر HL7
pending_results = []

def parse_hl7_message(hl7_raw):
    """
    تفكيك رسالة HL7 القياسية واستخراج الباركود والنتائج الطبية
    """
    lines = hl7_raw.strip().split('\n')
    barcode = ""
    results = []
    
    for line in lines:
        line = line.strip()
        parts = line.split('|')
        segment = parts[0]
        
        # OBR segment يحتوي على الباركود/معرف العينة
        if segment == 'OBR' and len(parts) > 3:
            barcode = parts[3].strip()
            
        # OBX segment يحتوي على اسم التحليل والنتيجة الرقمية والنطاق المرجعي
        elif segment == 'OBX' and len(parts) > 7:
            test_name = parts[3].replace('^', ' ').strip()
            value = parts[5].strip()
            units = parts[6].strip()
            ref_range = parts[7].strip()
            results.append(f"• {test_name}: {value} {units} (المعدل: {ref_range})")
            
    return barcode, "\n".join(results)

@app.route('/api/port-data', methods=['GET'])
def get_incoming_results():
    """الموقع يسحب النتائج من هنا تلقائياً كل ثانيتين"""
    global pending_results
    data = list(pending_results)
    pending_results.clear()
    return jsonify({"success": True, "readings": data})

@app.route('/api/hl7-receive', methods=['POST'])
def receive_hl7():
    """هنا يستقبل السيرفر رسائل الـ HL7 القادمة من محاكي الجهاز"""
    req = request.json or {}
    hl7_text = req.get("hl7_message", "")
    
    if not hl7_text:
        return jsonify({"success": False, "error": "HL7 message empty"}), 400
        
    barcode, formatted_result = parse_hl7_message(hl7_text)
    
    if barcode:
        payload = {
            "barcode": barcode,
            "raw_hl7": hl7_text,
            "clinical_result": formatted_result
        }
        pending_results.append(payload)
        print(f"\n[+] HL7 Ingested successfully for Barcode: {barcode}")
        print(f"--- Decoded Result ---\n{formatted_result}\n----------------------")
        return jsonify({"success": True, "matched_barcode": barcode})
    
    return jsonify({"success": False, "error": "No barcode found in OBR"}), 400

if __name__ == '__main__':
    print("[*] مستمع أجهزة المختبر (HL7 Listener) يعمل الآن على http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)