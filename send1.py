import requests

# ===== تنظیمات را اینجا وارد کن =====
TOKEN = "317697879:AAH7aWVDWwyd6BOHn-dB7PhJnlFmHlGmOOA"
CHAT_ID = "297817539"
FILE_PATH = "/root/skirk_config.txt"   # مسیر فایل روی سرور
# ===================================

url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"

with open(FILE_PATH, "rb") as f:
    files = {"document": f}
    data = {"chat_id": CHAT_ID}
    response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    print("فایل با موفقیت ارسال شد.")
else:
    print("خطا:", response.text)
