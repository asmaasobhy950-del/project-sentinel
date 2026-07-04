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
def delete_task(db_config, task_name):
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    # تأكدي إن اسم الجدول عندك هو tasks
    cur.execute("DELETE FROM tasks WHERE task_name = %s", (task_name,))
    conn.commit()
    cur.close()
    conn.close()

def update_task(db_config, old_task_name, new_name, assigned, contact, deadline, status):
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""
        UPDATE tasks 
        SET task_name = %s, assigned_to = %s, contact_info = %s, deadline = %s, status = %s
        WHERE task_name = %s
    """, (new_name, assigned, contact, deadline, status, old_task_name))
    conn.commit()
    cur.close()
    conn.close()