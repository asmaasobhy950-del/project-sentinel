import streamlit as st
import os
from agent_core import add_new_task, get_overdue_tasks # استدعاء الدوال المطلوبة

# إعداد الصفحة
st.set_page_config(page_title="Project Sentinel", layout="wide")
st.title("🤖 Project Sentinel")

# تهيئة الاتصال (مظلة الأمان)
if 'db_config' not in st.session_state:
    try:
        st.session_state['db_config'] = {
            "host": st.secrets['DB_HOST'],
            "database": st.secrets['DB_NAME'],
            "user": st.secrets['DB_USER'],
            "password": st.secrets['DB_PASS']
        }
    except:
        st.session_state['db_config'] = None

tab1, tab2, tab3 = st.tabs(["🔗 الإعدادات", "📊 تشغيل الـ Agent", "➕ إدارة المهام"])

with tab3:
    st.header("➕ إضافة مهمة جديدة")
    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input("اسم المهمة")
        assigned_to = st.text_input("المسند إليه")
        deadline = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة المهمة")

    if submit:
        config = st.session_state.get('db_config')
        if config and task_name and assigned_to:
            try:
                # إرسال 5 قيم كاملة (db_config, name, assigned, deadline, status)
                add_new_task(config, task_name, assigned_to, str(deadline), "In Progress")
                st.success("✅ تمت إضافة المهمة بنجاح!")
            except Exception as e:
                st.error(f"خطأ في قاعدة البيانات: {e}")
        else:
            st.error("❌ تأكد من الاتصال ومن ملء كافة الحقول.")