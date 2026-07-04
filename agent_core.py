import psycopg2
from psycopg2 import pool
import pandas as pd
import streamlit as st

@st.cache_resource
def get_connection_pool(db_config):
    return psycopg2.pool.SimpleConnectionPool(1, 10, **db_config)

def init_db(db_config):
    db_pool = get_connection_pool(db_config)
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS tasks (id SERIAL PRIMARY KEY, project_name TEXT, task_name TEXT, assigned_to TEXT, contact_info TEXT, deadline TEXT, status TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS audit_logs (id SERIAL PRIMARY KEY, action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, action_type TEXT, task_name TEXT, details TEXT)")
        conn.commit()
        cur.close()
    finally:
        db_pool.putconn(conn)

def log_action(db_pool, action_type, task_name, details):
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO audit_logs (action_type, task_name, details) VALUES (%s, %s, %s)", (action_type, task_name, details))
        conn.commit()
        cur.close()
    finally:
        db_pool.putconn(conn)

def clear_audit_logs(db_config):
    db_pool = get_connection_pool(db_config)
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM audit_logs")
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

def add_new_task(db_config, project_name, name, assigned, contact, deadline, status):
    db_pool = get_connection_pool(db_config)
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (project_name, task_name, assigned_to, contact_info, deadline, status) VALUES (%s, %s, %s, %s, %s, %s)", 
                    (project_name, name, assigned, contact, deadline, status))
        conn.commit()
        log_action(db_pool, "إضافة", name, f"مشروع: {project_name}")
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
        log_action(db_pool, "حذف", task_name, "تم الحذف")
        cur.close()
    finally:
        db_pool.putconn(conn)