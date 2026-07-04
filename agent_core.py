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
        print("تم إرسال الimport psycopg2
from psycopg2 import pool
import pandas as pd
import streamlit as st

# إنشاء Pool للاتصالات وتخزينه في الكاش لتجنب إنشائه مراراً
@st.cache_resource
def get_connection_pool(db_config):
    return psycopg2.pool.SimpleConnectionPool(1, 10, **db_config)

def get_all_tasks(db_config):
    db_pool = get_connection_pool(db_config)
    conn = db_pool.getconn()
    try:
        query = "SELECT * FROM tasks"
        df = pd.read_sql(query, conn)
        return df
    finally:
        db_pool.putconn(conn) # إرجاع الاتصال للحوض

def add_new_task(db_config, name, assigned, contact, deadline, status):
    db_pool = get_connection_pool(db_config)
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tasks (task_name, assigned_to, contact_info, deadline, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, assigned, contact, deadline, status))
        conn.commit()
        cur.close()
    finally:
        db_pool.putconn(conn)

def update_task(db_config, old_task_name, new_name, assigned, contact, deadline, status):
    db_pool = get_connection_pool(db_config)
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE tasks 
            SET task_name = %s, assigned_to = %s, contact_info = %s, deadline = %s, status = %s
            WHERE task_name = %s
        """, (new_name, assigned, contact, deadline, status, old_task_name))
        conn.commit()
        cur.close()
    finally:
        db_pool.putconn(conn)

def delete_task(db_config, task_name):
    db_pool = get_connection_pool(db_config)
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE task_name = %s", (task_name,))
        conn.commit()
        cur.close()
    finally:
        db_pool.putconn(conn)تقرير بنجاح.")
    else:
        print("لا توجد مهام معلقة اليوم.")