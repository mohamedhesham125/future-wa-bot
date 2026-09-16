"""
Future Systems - WhatsApp Automation V3
Company Number: +1-555-148-7654 / +20 15 50319154
Phone Number ID: 1304470152756918
"""

import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# === CONFIG ===
PHONE_NUMBER_ID = "1304470152756918"
COMPANY_NUMBER = "+1-555-148-7654"
ALLOWED_NUMBERS = ["201550319154", "12013880044"] # المصري + الأمريكي - نظفهم بعدين
ACCESS_TOKEN = os.getenv("WA_TOKEN")

PRICE_PER_USER = 1500
PRICE_PER_BRANCH = 750
NATIONAL_DAY_DISCOUNT = 0.5

def calculate_price(users, branches):
    original = (users * PRICE_PER_USER) + (branches * PRICE_PER_BRANCH)
    discounted = original * (1 - NATIONAL_DAY_DISCOUNT)
    return original, discounted

def send_document(to, file_url):
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

@app.route("/")
def home():
    return "Future Systems Bot is Running ✅"

@app.route("/webhook", methods=["GET"])
def verify():
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
        from_number = msg['from']
        text = msg['text']['body'] if msg['type'] == 'text' else ""

        print(f"INCOMING: {from_number}: {text}")

        # فلتر تجريبي - احذفه بعد التجربة
        # if from_number not in ALLOWED_NUMBERS:
        #     print(f"IGNORED: {from_number}")
        #     return "Ignored", 200

        if "اسطول" in text or "نقل" in text or "fleet" in text.lower():
            drive_link = "https://drive.google.com/uc?export=download&id=YOUR_FILE_ID"
            send_document(from_number, drive_link)
            
            questions = """أهلاً بك في Future Systems 👋

عشان أبعتلك عرض سعر دقيق:
1- ما هو نشاط الشركة؟ (نقل حديد / خرسانة / عام)
2- كم عدد المستخدمين وعدد الفروع؟
3- ممكن صورة السجل التجاري؟"""
            send_message(from_number, questions)

        elif "مستخدمين" in text and "فروع" in text:
            import re
            users_m = re.search(r'(\d+)\s*مستخدم', text)
            branches_m = re.search(r'(\d+)\s*فروع', text)
            users = int(users_m.group(1)) if users_m else 3
            branches = int(branches_m.group(1)) if branches_m else 3
            
            original, discounted = calculate_price(users, branches)
            
            reply = f"""تم ✅

نشاط: نقل حديد
المستخدمين: {users} × {PRICE_PER_USER} = {users*PRICE_PER_USER}
الفروع: {branches} × {PRICE_PER_BRANCH} = {branches*PRICE_PER_BRANCH}
الإجمالي قبل الخصم: {original} ريال

بعد خصم 50% اليوم الوطني 🇸🇦: *{discounted} ريال*

[تنبيه داخلي: عدّل قالب كانفا 610199]"""
            send_message(from_number, reply)

    except Exception as e:
        print(f"Error: {e}")

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
