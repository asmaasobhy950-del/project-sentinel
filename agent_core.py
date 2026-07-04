import psycopg2
import pandas as pd

def get_all_tasks(db_config):
    conn = psycopg2.connect(**db_config)
    # جلب كافة الأعمدة التي تظهر في جدولك
    query = "SELECT task_name, assigned_to, contact_info, deadline, status FROM tasks"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def add_new_task(db_config, task_name, assigned_to, contact_info, deadline, status):
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    query = """INSERT INTO tasks (task_name, assigned_to, contact_info, deadline, status) 
               VALUES (%s, %s, %s, %s, %s)"""
    cur.execute(query, (task_name, assigned_to, contact_info, deadline, status))
    conn.commit()
    cur.close()
    conn.close()