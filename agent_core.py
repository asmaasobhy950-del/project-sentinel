import psycopg2
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

def add_new_task(db_config, name, assigned, contact, deadline, status, company, project):
    db_pool = get_connection_pool(db_config)
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tasks (task_name, assigned_to, contact_info, deadline, status, company_name, project_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, assigned, contact, deadline, status, company, project))
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
        db_pool.putconn(conn)