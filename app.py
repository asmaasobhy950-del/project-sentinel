import streamlit as st
import os
from agent_core import get_overdue_tasks, generate_ai_report, add_new_task, update_task_status

# 1. أول خطوة: تعريف التبويبات (هذا السطر لازم يكون قبل استخدامهم)
tab1, tab2, tab3 = st.tabs(["🔗 الإعدادات", "📊 تشغيل الـ Agent", "➕ إدارة المهام"])

# 2. الآن يمكنك استخدام كل تبويب بالترتيب
with tab1:
    st.header("إعدادات الاتصال")
    # ... كود الإعدادات ...

with tab2:
    st.header("تشغيل الـ Agent")
    # ... كود الـ Agent ...

with tab3:
    st.header("➕ إضافة مهمة جديدة")
    # ... كود إضافة المهام ...
# دالة أمان لقراءة البيانات
def get_secret(key):
    return st.secrets.get(key) or os.getenv(key)

# "مظلة الأمان": تهيئة الاتصال وتخزينه في الـ session_state بشكل دائم
if 'db_config' not in st.session_state:
    db_host = get_secret('DB_HOST')
    if db_host:
        st.session_state['db_config'] = {
            "host": db_host,
            "database": get_secret('DB_NAME'),
            "user": get_secret('DB_USER'),
            "password": get_secret('DB_PASS')
        }

# --- الآن في التبويب الثالث (إدارة المهام) ---
with tab3:
    st.header("➕ إضافة مهمة جديدة")
    
    with st.form("add_task_form"):
        task_name = st.text_input("اسم المهمة")
        assigned_to = st.text_input("المسند إليه")
        deadline = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة المهمة")
        
        if submit:
            # التحقق من وجود الاتصال قبل التنفيذ
            if 'db_config' in st.session_state:
                if task_name and assigned_to:
                    add_new_task(st.session_state['db_config'], task_name, assigned_to, str(deadline))
                    st.success(f"تم إضافة المهمة: {task_name}")
                else:
                    st.error("من فضلك املأ البيانات الأساسية.")
            else:
                st.error("خطأ: لم يتم تهيئة قاعدة البيانات. تأكد من الإعدادات.")
            
