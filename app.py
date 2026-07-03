import streamlit as st
import os
from agent_core import get_overdue_tasks, generate_ai_report, add_new_task, update_task_status

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="Project Sentinel", layout="wide")

# 2. تهيئة الـ Session State للاتصال (مرة واحدة فقط)
if 'db_config' not in st.session_state:
    try:
        st.session_state['db_config'] = {
            "host": st.secrets['DB_HOST'],
            "database": st.secrets['DB_NAME'],
            "user": st.secrets['DB_USER'],
            "password": st.secrets['DB_PASS']
        }
    except Exception as e:
        st.session_state['db_config'] = None

# 3. واجهة التبويبات
tab1, tab2, tab3 = st.tabs(["🔗 الإعدادات", "📊 تشغيل الـ Agent", "➕ إدارة المهام"])

# --- التبويب الأول: الإعدادات ---
with tab1:
    st.header("إعدادات الاتصال")
    if st.session_state.get('db_config'):
        st.success("✅ متصل بقاعدة البيانات بنجاح!")
    else:
        st.error("❌ فشل الاتصال. تأكد من إعدادات الـ Secrets.")

# --- التبويب الثاني: تشغيل الـ Agent ---
with tab2:
    st.header("📊 تشغيل الـ Agent")
    if st.button("🚀 فحص المهام"):
        config = st.session_state.get('db_config')
        if config:
            tasks = get_overdue_tasks(config)
            st.write(tasks)
        else:
            st.error("لا يوجد اتصال متاح.")

# --- التبويب الثالث: إدارة المهام ---
with tab3:
    st.header("➕ إضافة مهمة جديدة")
    
    # استخدام clear_on_submit بيمسح البيانات بعد الإضافة لمنع أي تعارض
    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input("اسم المهمة")
        assigned_to = st.text_input("المسند إليه")
        deadline = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة المهمة")
        
        # التنفيذ محمي داخل شرط الزرار
        if submit:
            config = st.session_state.get('db_config')
            if config and task_name and assigned_to:
                # استدعاء الدالة هنا فقط بعد التأكد من البيانات
                add_new_task(config, task_name, assigned_to, str(deadline))
                st.success(f"✅ تمت إضافة المهمة: {task_name}")
            elif not config:
                st.error("❌ خطأ: لا يوجد اتصال بقاعدة البيانات.")
            else:
                st.warning("⚠️ يرجى إدخال اسم المهمة والشخص المسؤول.")