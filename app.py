import streamlit as st
import os
from agent_core import get_overdue_tasks, generate_ai_report, add_new_task, update_task_status

# --- مسح الكاش القديم لضمان البدء من جديد ---
# إذا كنت بتواجه إيرور مستمر، فك التعليق عن السطر ده مرة واحدة فقط
# st.session_state.clear() 

# 1. إعدادات الصفحة
st.set_page_config(page_title="Project Sentinel", layout="wide", page_icon="🤖")
st.title("🤖 Project Sentinel :لوحة تحكم الوكيل الذكي")

# 2. تعريف التبويبات
tab1, tab2, tab3 = st.tabs(["🔗 الإعدادات", "📊 تشغيل الـ Agent", "➕ إدارة المهام"])

# 3. دالة تهيئة الاتصال - أكثر صرامة
def init_db():
    if 'db_config' not in st.session_state:
        try:
            # قراءة مباشرة من الـ secrets
            st.session_state['db_config'] = {
                "host": st.secrets['DB_HOST'],
                "database": st.secrets['DB_NAME'],
                "user": st.secrets['DB_USER'],
                "password": st.secrets['DB_PASS']
            }
        except Exception:
            st.session_state['db_config'] = None

init_db()

# --- التبويب الأول: الإعدادات ---
with tab1:
    st.header("إعدادات الاتصال")
    if st.session_state.get('db_config'):
        st.success("✅ متصل بقاعدة البيانات!")
    else:
        st.error("❌ فشل الاتصال. تأكد من الـ Secrets.")

# --- التبويب الثالث: إدارة المهام ---
with tab3:
    st.header("➕ إضافة مهمة جديدة")
    
    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input("اسم المهمة")
        assigned_to = st.text_input("المسند إليه")
        deadline = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة المهمة")
        
        if submit:
            config = st.session_state.get('db_config')
            if config:
                if task_name and assigned_to:
                    add_new_task(config, task_name, assigned_to, str(deadline))
                    st.success("✅ تمت الإضافة!")
                else:
                    st.warning("⚠️ يرجى ملء البيانات.")
            else:
                st.error("❌ لا يوجد اتصال.")