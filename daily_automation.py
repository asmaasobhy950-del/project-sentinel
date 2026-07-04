import psycopg2
import pandas as pd
import requests

# 1. إعدادات قاعدة البيانات (PostgreSQL)
db_config = {
    "host": "your_db_host",
    "database": "your_db_name",
    "user": "your_db_user",
    "password": "your_db_password"
}

# 2. إعدادات Telegram Bot (للتنبيهات التلقائية الآمنة للمدير)
# يمكنك إنشاء بوت مجاني من @BotFather على تيليجرام
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def fetch_pending_tasks():
    conn = psycopg2.connect(**db_config)
    query = "SELECT task_name, assigned_to, deadline FROM tasks WHERE status != 'Done'"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    df = fetch_pending_tasks()
    
    if not df.empty:
        report = "🚨 **تقرير المهام غير المكتملة الصباحي** 🚨\n\n"
        for index, row in df.iterrows():
            report += f"- المهمة: {row['task_name']} | الموظف: {row['assigned_to']} | موعد التسليم: {row['deadline']}\n"
        
        # إرسال التقرير التلقائي
        send_telegram_alert(report)
        print("تم إرسال التقرير بنجاح.")
    else:
        print("لا توجد مهام معلقة اليوم.")