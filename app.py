import streamlit as st
import os
from agent_core import get_overdue_tasks, add_new_task

# 1. إعداد الاتصال بشكل آمن ومعزول
@st.cache_resource
def get_db_connection():
    try:
        return {
            "host": st.secrets['DB_HOST'],
            "database": st.secrets['DB_NAME'],
            "user": st.secrets['DB_USER'],
            "password": st.secrets['DB_PASS']
        }
    except:
        return None

st.set_page_config(page_title="Project Sentinel", layout="wide")
st.title("🤖 Project Sentinel")

# ربط الاتصال
db_config = get_db_connection()

tab1, tab2, tab3 = st.tabs(["🔗 الإعدادات", "📊 تشغيل الـ Agent", "➕ إدارة المهام"])

with tab1:
    if db_config:
        st.success("✅ متصل بقاعدة البيانات")
    else:
        st.error("❌ فشل الاتصال (تأكد من الـ Secrets)")

with tab2:
    if st.button("🚀 فحص المهام"):
        if db_config:
            st.write(get_overdue_tasks(db_config))
        else:
            st.error("لا يوجد اتصال")

with tab3:
    with st.form("add_task_form"):
        task_name = st.text_input("اسم المهمة")
        assigned_to = st.text_input("المسند إليه")
        deadline = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة المهمة")

    if submit:
        # هنا التأكد الكامل قبل التنفيذ
        if db_config and task_name and assigned_to:
            try:
                add_new_task(db_config, task_name, assigned_to, str(deadline))
                st.success("✅ تمت الإضافة!")
            except Exception as e:
                st.error(f"خطأ في قاعدة البيانات: {e}")
        else:
            st.error("بيانات ناقصة أو لا يوجد اتصال!")