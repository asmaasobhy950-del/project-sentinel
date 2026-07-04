import psycopg2
from psycopg2 import pool
import pandas as pd
import streamlit as st
from datetime import datetime

# إعداد حوض الاتصالات (Connection Pool)
@st.cache_resource
def get_connection_pool(db_config):
    return psycopg2.pool.SimpleConnectionPool(1, 10, **db_config)

def log_action(db_pool, action_type, task_name, details):
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS audit_logs (id SERIAL PRIMARY KEY, action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, action_type TEXT, task_name TEXT, details TEXT)")
        cur.execute("INSERT INTO audit_logs (action_type, task_name, details) VALUES (%s, %s, %s)", (action_type, task_name, details))
        conn.commit()
        cur.close()
    finally:
        db_pool.putconn(conn)

def get_all_tasks(db_config):
    db_pool = get_connection_pool(db_config)
    conn = db_pool.getconn()
    try:
        return pd.read_sql("SELECT * FROM tasks", conn)
    finally:
        db_pool.putconn(conn)

def get_audit_logs(db_config):
    db_pool = get_connection_pool(db_config)
    conn = db_pool.getconn()
    try:
        return pd.read_sql("SELECT * FROM audit_logs ORDER BY action_time DESC LIMIT 50", conn)
    finally:
        db_pool.putconn(conn)

def add_new_task(db_config, name, assigned, contact, deadline, status):
    db_pool = get_connection_pool(db_config)
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (task_name, assigned_to, contact_info, deadline, status) VALUES (%s, %s, %s, %s, %s)", (name, assigned, contact, deadline, status))
        conn.commit()
        log_action(db_pool, "إضافة", name, f"مهمة جديدة لـ {assigned}")
    finally:
        db_pool.putconn(conn)

def update_task(db_config, old_name, n_name, assigned, contact, deadline, status):
    db_pool = get_connection_pool(db_config)
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE tasks SET task_name=%s, assigned_to=%s, contact_info=%s, deadline=%s, status=%s WHERE task_name=%s", (n_name, assigned, contact, deadline, status, old_name))
        conn.commit()
        log_action(db_pool, "تعديل", n_name, f"تعديل الحالة لـ {status}")
    finally:
        db_pool.putconn(conn)

def delete_task(db_config, task_name):
    db_pool = get_connection_pool(db_config)
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE task_name = %s", (task_name,))
        conn.commit()
        log_action(db_pool, "حذف", task_name, "تم الحذف نهائياً")
    finally:
        db_pool.putconn(conn)