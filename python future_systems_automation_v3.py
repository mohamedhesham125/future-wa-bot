"""
Future Systems - WhatsApp Automation V3
Company Number: +1-555-148-7654
Phone Number ID: 1304470152756918
Test Mode: ONLY +20 15 50319154 allowed
"""

import os
from flask import Flask, request, jsonify
import requests

# === CONFIG (اللي انت حددته) ===
PHONE_NUMBER_ID = "1304470152756918"
COMPANY_NUMBER = "+1-555-148-7654"  # رقم الشركة الأمريكي اللي بيبعت
ALLOWED_NUMBERS = ["201550319154"] # المصري بس - الفلتر التجريبي
ACCESS_TOKEN = os.getenv("WA_TOKEN") # هنحطه في .env

# Drive & Canva
CATALOG_DRIVE_FILE = "Future Systems - All Systems Catalog.pdf"
CANVA_TEMPLATES = {
    "fleet": "610199",
    "generic": "610198",
    "real_estate": "610120",
    "logistics": "610199"
}

# Pricing V3 - المعادلة الجديدة
PRICE_PER_USER = 1500
PRICE_PER_BRANCH = 750 # نص سعر المستخدم
NATIONAL_DAY_DISCOUNT = 0.5 # خصم 50%

def calculate_price(users, branches):
    original = (users * PRICE_PER_USER) + (branches * PRICE_PER_BRANCH)
    discounted = original * (1 - NATIONAL_DAY_DISCOUNT)
    return original, discounted

# === WHATSAPP SEND FUNCTIONS ===
def send_document(to, file_url):
    """يبعت الكتالوج كملف مش لينك"""
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "document",
        "document": {
            "link": file_url,
            "filename": "Future Systems - All Systems Catalog.pdf"
        }
    }
    return requests.post(url, json=payload, headers=headers)

def send_message(to, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    return requests.post(url, json=payload, headers=headers)

# === FLASK WEBHOOK ===
app = Flask(__name__)

@app.route("/webhook", methods=["GET"])
def verify():
    # للـ Verification من Meta
    if request.args.get("hub.verify_token") == "future123":
        return request.args.get("hub.challenge")
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        entry = data['entry'][0]['changes'][0]['value']
        if 'messages' not in entry:
            return "No message", 200
        
        msg = entry['messages'][0]
        from_number = msg['from'] # مثال: 201550319154
        text = msg['text']['body'] if msg['type'] == 'text' else ""

        print(f"INCOMING: {from_number} -> {COMPANY_NUMBER}: {text}")

        # === فلتر الوضع التجريبي ===
        if from_number not in ALLOWED_NUMBERS:
            print(f"IGNORED: {from_number} not in whitelist")
            return "Ignored - Not whitelisted", 200

        # === الرد الأوتوماتيكي ===
        # لو العميل قال أسطول / نقل
        if "اسطول" in text or "نقل" in text or "fleet" in text.lower():
            # 1- ابعت الكتالوج كملف (لينك درايف مباشر)
            drive_link = "https://drive.google.com/uc?export=download&id=YOUR_FILE_ID"
            send_document(from_number, drive_link)
            
            # 2- ابعت الـ 3 أسئلة
            questions = """أهلاً بك في Future Systems 👋

عشان أبعتلك عرض سعر دقيق:
1- ما هو نشاط الشركة؟ (نقل حديد / خرسانة / عام)
2- كم عدد المستخدمين وعدد الفروع؟
3- ممكن صورة السجل التجاري؟"""
            send_message(from_number, questions)

        # لو رد بالأعداد
        elif "مستخدمين" in text and "فروع" in text:
            # مثال: "3 مستخدمين 3 فروع"
            import re
            users = int(re.search(r'(\d+)\s*مستخدم', text).group(1)) if re.search(r'(\d+)\s*مستخدم', text) else 3
            branches = int(re.search(r'(\d+)\s*فروع', text).group(1)) if re.search(r'(\d+)\s*فروع', text) else 3
            
            original, discounted = calculate_price(users, branches)
            
            reply = f"""تم ✅

نشاط: نقل حديد
المستخدمين: {users} × {PRICE_PER_USER} = {users*PRICE_PER_USER}
الفروع: {branches} × {PRICE_PER_BRANCH} = {branches*PRICE_PER_BRANCH}
الإجمالي قبل الخصم: {original} ريال

بعد خصم 50% اليوم الوطني 🇸🇦: *{discounted} ريال*

[تنبيه داخلي: عدّل قالب كانفا {CANVA_TEMPLATES['fleet']}]"""
            send_message(from_number, reply)

    except Exception as e:
        print(f"Error: {e}")

    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)

# === تعليمات التشغيل ===
# 1- حط التوكن في ملف .env: WA_TOKEN=EAAP0XC...
# 2- شغل: python future_systems_automation_v3.py
# 3- في Meta Developers: Webhook URL = https://yourdomain.com/webhook
# 4- Verify Token = future123
