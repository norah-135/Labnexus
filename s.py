import requests
import time
import sys

# الرابط الخاص بالمستمع الدائم
LISTENER_URL = "http://localhost:5000/api/hl7-receive"

def build_hl7_message(barcode, test_type="TOX"):
    """
    بناء رسالة طبية قياسية موحدة (HL7 v2.5 Standard Message)
    """
    timestamp = time.strftime("%Y%m%d%H%M%S")
    
    if "101" in barcode or "TOX" in test_type.upper() or "سموم" in test_type:
        # رسالة HL7 لتحليل السموم
        hl7 = f"""MSH|^~\\&|COBAS_6000|BURAYDAH_CENTRAL_LAB|LABNEXUS|MOH|{timestamp}||ORU^R01|MSG{int(time.time())}|P|2.5
PID|1||8812^^^PRISON_REF||نزيل مجهول||19880101|M
OBR|1||{barcode}|TOX^Toxicology Screen Panel|||{timestamp}
OBX|1|ST|AMP^Amphetamine/Meth Screen||Negative|ng/mL|< 500|N|||F
OBX|2|ST|THC^Cannabinoids Screen||Negative|ng/mL|< 50|N|||F
OBX|3|ST|OPI^Opiates Screen||Negative|ng/mL|< 300|N|||F
OBX|4|ST|BZO^Benzodiazepines||Negative|ng/mL|< 200|N|||F"""
    else:
        # رسالة HL7 لتحليل الدم CBC
        hl7 = f"""MSH|^~\\&|SYSMEX_XN|BURAYDAH_CENTRAL_LAB|LABNEXUS|MOH|{timestamp}||ORU^R01|MSG{int(time.time())}|P|2.5
PID|1||4410^^^PRISON_REF||نزيل مجهول||19940512|M
OBR|1||{barcode}|CBC^Complete Blood Count|||{timestamp}
OBX|1|NM|HGB^Hemoglobin||14.7|g/dL|13.5-17.5|N|||F
OBX|2|NM|WBC^White Blood Cells||6.3|10^3/uL|4.5-11.0|N|||F
OBX|3|NM|PLT^Platelets||240|10^3/uL|150-450|N|||F
OBX|4|NM|RBC^Red Blood Cells||4.85|10^6/uL|4.3-5.9|N|||F"""
    
    return hl7

def send_test_sample(barcode):
    print(f"[*] جاري إنشاء رسالة HL7 للجهاز للعينة: {barcode}...")
    hl7_msg = build_hl7_message(barcode)
    
    try:
        response = requests.post(LISTENER_URL, json={"hl7_message": hl7_msg})
        if response.status_code == 200:
            print(f"[✓] نجاح: تم إرسال رسالة HL7 من جهاز التحليل للمستمع بنجاح!")
        else:
            print(f"[!] خطأ في الإرسال: {response.text}")
    except Exception as e:
        print(f"[X] تعذر الاتصال بالمستمع. تأكد من تشغيل analyzer_bridge.py أولاً! ({e})")

if __name__ == '__main__':
    # يمكنك تمرير الباركود من سطر الأوامر أو الإرسال الافتراضي للعينة المعلقة
    target_barcode = sys.argv[1] if len(sys.argv) > 1 else "SMP-RHB-7578"
    send_test_sample(target_barcode)