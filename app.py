import streamlit as st
import os
from agent_core import get_overdue_tasks, generate_ai_report, add_new_task, update_task_status

# 1. إعدادات الصفحة
st.set_page_config(page_title="Project Sentinel", layout="wide", page_icon="🤖")
st.title("🤖 Project Sentinel :لوحة تحكم الوكيل الذكي")

# 2. تعريف التبويبات (لازم يكون قبل الاستخدام)
tab1, tab2, tab3 = st.tabs(["🔗 الإعدادات", "📊 تشغيل الـ Agent", "➕ إدارة المهام"])

# 3. دالة آمنة لقراءة الـ Secrets
def get_secret(key):
    return st.secrets.get(key) or os.getenv(key)

# 4. تهيئة الاتصال وتخزينه في الـ session_state (مظلة الأمان)
if 'db_config' not in st.session_state:
    db_host = get_secret('DB_HOST')
    if db_host:
        st.session_state['db_config'] = {
            "host": db_host,
            "database": get_secret('DB_NAME'),
            "user": get_secret('DB_USER'),
            "password": get_secret('DB_PASS')
        }

# --- التبويب الأول: الإعدادات ---
with tab1:
    st.header("إعدادات الاتصال")
    if 'db_config' in st.session_state:
        st.success("✅ تم الاتصال بقاعدة البيانات بنجاح!")
    else:
        st.warning("⚠️ يرجى ضبط الـ Secrets في إعدادات التطبيق.")

# --- التبويب الثاني: تشغيل الـ Agent ---
with tab2:
    st.header("📊 تشغيل الـ Agent")
    if 'db_config' in st.session_state:
        if st.button("🚀 فحص المهام"):
            with st.spinner("جاري فحص المهام..."):
                tasks = get_overdue_tasks(st.session_state['db_config'])
                st.write(tasks)
    else:
        st.error("لا يمكن الوصول لقاعدة البيانات. ارجع لتبويب الإعدادات.")

# --- التبويب الثالث: إدارة المهام ---
with tab3:
    st.header("➕ إضافة مهمة جديدة")
    
    with st.form("add_task_form"):
        task_name = st.text_input("اسم المهمة")
        assigned_to = st.text_input("المسند إليه")
        deadline = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة المهمة")
        
        # التنفيذ محمي داخل شرط الزرار
        if submit:
            if 'db_config' in st.session_state:
                if task_name and assigned_to:
                    add_new_task(st.session_state['db_config'], task_name, assigned_to, str(deadline))
                    st.success(f"تمت إضافة المهمة: {task_name} بنجاح!")
                else:
                    st.error("من فضلك املأ كافة الحقول.")
            else:
                st.error("خطأ: لا يوجد اتصال بقاعدة البيانات.")