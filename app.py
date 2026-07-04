import streamlit as st
from agent_core import add_new_task, get_all_tasks

st.set_page_config(page_title="Project Sentinel", layout="wide")

# 1. حل مشكلة الـ KeyError (التعامل الآمن مع الـ Secrets)
def get_db_config():
    try:
        return {
            "host": st.secrets["DB_HOST"],
            "database": st.secrets["DB_NAME"],
            "user": st.secrets["DB_USER"],
            "password": st.secrets["DB_PASS"]
        }
    except Exception:
        return None

db_config = get_db_config()

tab1, tab2, tab3 = st.tabs(["📊 الداشبورد", "🤖 تقارير Gemini", "➕ إضافة مهام"])

# --- التبويب 3: إضافة المهام (التعديل المهم) ---
with tab3:
    st.header("➕ إضافة مهمة جديدة")
    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input("اسم المهمة")
        assigned_to = st.text_input("المسند إليه")
        contact_info = st.text_input("معلومات التواصل")
        status = st.selectbox("الحالة", ["Pending", "In Progress", "Done"])
        deadline = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة المهمة")

    # التنفيذ الآمن
    if submit:
        if db_config and task_name and assigned_to:
            try:
                # إرسال 6 بارامترات كاملة (تأكدي إن دالة agent_core.py بتستقبلهم بنفس الترتيب)
                add_new_task(db_config, task_name, assigned_to, contact_info, str(deadline), status)
                st.success("✅ تمت الإضافة بنجاح!")
            except Exception as e:
                st.error(f"خطأ في قاعدة البيانات: {e}")
        else:
            st.warning("⚠️ يرجى التأكد من ملء كافة البيانات.")

# --- التبويب 1: الداشبورد ---
with tab1:
    st.header("📊 حالة المهام")
    if db_config:
        df = get_all_tasks(db_config)
        st.dataframe(df)
    else:
        st.error("خطأ في الاتصال بالبيانات - تأكدي من الـ Secrets.")