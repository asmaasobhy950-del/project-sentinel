import streamlit as st
import os
from agent_core import get_overdue_tasks, generate_ai_report, add_new_task, update_task_status

# 1. تهيئة الـ Tabs (لازم تكون في البداية)
tab1, tab2, tab3 = st.tabs(["🔗 الإعدادات", "📊 تشغيل الـ Agent", "➕ إدارة المهام"])

# 2. دالة لقراءة البيانات
def get_secret(key):
    return st.secrets.get(key) or os.getenv(key)

# 3. تهيئة الاتصال (في الـ Session State)
if 'db_config' not in st.session_state:
    db_host = get_secret('DB_HOST')
    if db_host:
        st.session_state['db_config'] = {
            "host": db_host,
            "database": get_secret('DB_NAME'),
            "user": get_secret('DB_USER'),
            "password": get_secret('DB_PASS')
        }

with tab1:
    st.header("إعدادات الاتصال")
    if 'db_config' in st.session_state:
        st.success("✅ تم الاتصال بقاعدة البيانات بنجاح!")
    else:
        st.warning("⚠️ يرجى ضبط الـ Secrets في إعدادات التطبيق.")

with tab2:
    st.header("تشغيل الـ Agent")
    if 'db_config' in st.session_state:
        if st.button("🚀 فحص المهام"):
            tasks = get_overdue_tasks(st.session_state['db_config'])
            st.write(tasks)
    else:
        st.error("لا يوجد اتصال بقاعدة البيانات.")

with tab3:
    st.header("➕ إضافة مهمة جديدة")
    # الـ Form بتضمن إن الكود مش هيشتغل غير لما تضغط الزرار
    with st.form("add_task_form"):
        task_name = st.text_input("اسم المهمة")
        assigned_to = st.text_input("المسند إليه")
        deadline = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة المهمة")
        
        if submit:
            # هنا الكود بيتشيك إن الاتصال موجود قبل ما يستدعي الدالة
            if 'db_config' in st.session_state:
                if task_name and assigned_to:
                    add_new_task(st.session_state['db_config'], task_name, assigned_to, str(deadline))
                    st.success(f"تمت إضافة المهمة بنجاح!")
                else:
                    st.error("من فضلك أدخل كافة البيانات.")
            else:
                st.error("خطأ: لا يوجد اتصال بقاعدة البيانات.")