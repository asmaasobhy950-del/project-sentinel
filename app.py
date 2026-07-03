import streamlit as st
import os
from dotenv import load_dotenv
from agent_core import get_overdue_tasks, generate_ai_report, add_new_task, update_task_status

# استيراد آمن لدالة الواتساب
try:
    from notifier import send_whatsapp_reminder
except ImportError:
    send_whatsapp_reminder = None

load_dotenv()

st.set_page_config(page_title="Project Sentinel", layout="wide", page_icon="🤖")
st.title("🤖 Project Sentinel :لوحة تحكم الوكيل الذكي")

tab1, tab2, tab3 = st.tabs(["🔗 الإعدادات", "📊 تشغيل الـ Agent", "➕ إدارة المهام"])

# --- التبويب الأول ---
with tab1:
    st.header("إعدادات الاتصال")
    # (هنا حط الكود بتاعك بتاع الإعدادات اللي شغال)

# --- التبويب الثاني (تبويب الـ Agent) ---
with tab2:
    if 'db_config' in st.session_state:
        if st.button("🚀 فحص المهام"):
            tasks = get_overdue_tasks(st.session_state['db_config'])
            st.session_state['current_tasks'] = tasks
            st.write(tasks)
        
        # التعديل المهم هنا:
        if 'current_tasks' in st.session_state and st.session_state['current_tasks']:
            st.write("---")
            if send_whatsapp_reminder:
                if st.button("📱 إرسال تذكيرات الواتساب"):
                    # كود الإرسال
                    st.success("تم الإرسال!")
            else:
                st.info("ℹ️ ميزة الواتساب متاحة فقط للتشغيل المحلي على جهازك.")

# --- التبويب الثالث ---
with tab3:
    st.header("إدارة البيانات")
    # (هنا كود الـ CRUD اللي إنت عامله)
with tab1:
    st.header("إعدادات الاتصال")
    
    # محاولة قراءة البيانات من الـ Secrets (اللي إنت دخلتها في الموقع)
    if 'DB_HOST' in st.secrets:
        db_config = {
            "host": st.secrets['DB_HOST'],
            "database": st.secrets['DB_NAME'],
            "user": st.secrets['DB_USER'],
            "password": st.secrets['DB_PASS']
        }
        st.session_state['db_config'] = db_config
        st.success("✅ تم الاتصال بقاعدة البيانات بنجاح من الـ Secrets!")
    else:
        st.error("❌ لم يتم العثور على بيانات الاتصال في الـ Secrets. تأكد من إعداداتها.")