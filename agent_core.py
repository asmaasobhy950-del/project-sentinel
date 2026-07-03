import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import google.generativeai as genai
import json

def get_overdue_tasks(db_config):
    """جلب المهام المتأخرة من قاعدة البيانات"""
    query = """
        SELECT task_name, assigned_to, contact_info, deadline, status 
        FROM tasks 
        WHERE deadline < %s AND status != 'Completed';
    """
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query, (datetime.now().date(),))
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return tasks

def generate_ai_report(overdue_tasks, api_key):
    """تحليل البيانات وتوليد التقرير والرسائل بواسطة الذكاء الاصطناعي"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    أنت مدير مشروعات محترف وخبير بيانات. بناءً على المهام المتأخرة التالية، اكتب تقريراً إدارياً بالعامية المصرية المبسطة:
    {json.dumps(overdue_tasks, ensure_ascii=False, indent=2)}
    المطلوب:
    1. ملخص تنفيذي للمدير يوضح الموقف الحالي ونسب التأخير.
    2. صياغة رسايل تذكير ذكية ومحفزة (Friendly Reminders) لكل موظف باسمه ومهمته بشكل منفصل.
    """
    response = model.generate_content(prompt)
    return response.text
import psycopg2

def add_new_task(db_config, task_name, assigned_to, contact_info, deadline, status):
    """دالة لإضافة مهمة جديدة إلى قاعدة البيانات"""
    query = """
    INSERT INTO tasks (task_name, assigned_to, contact_info, deadline, status)
    VALUES (%s, %s, %s, %s, %s);
    """
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute(query, (task_name, assigned_to, contact_info, deadline, status))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding task: {e}")
        return False

def update_task_status(db_config, task_name, new_status, new_phone=None):
    """دالة لتحديث حالة المهمة أو رقم الهاتف باستخدام اسم المهمة"""
    if new_phone:
        query = "UPDATE tasks SET status = %s, contact_info = %s WHERE task_name = %s;"
        params = (new_status, new_phone, task_name)
    else:
        query = "UPDATE tasks SET status = %s WHERE task_name = %s;"
        params = (new_status, task_name)
        
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating task: {e}")
        return False
    import psycopg2

def add_new_task(db_config, task_name, assigned_to, deadline, status):
    conn = None
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        # تأكد إن الجدول عندك اسمه 'tasks' والأعمدة مطابقة
        query = "INSERT INTO tasks (task_name, assigned_to, deadline, status) VALUES (%s, %s, %s, %s)"
        cur.execute(query, (task_name, assigned_to, deadline, status))
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Database error: {e}")
        raise e # عشان الـ app يبين لنا الخطأ لو حصل
    finally:
        if conn:
            conn.close()