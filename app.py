import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px
import urllib.parse
from agent_core import add_new_task, get_all_tasks, delete_task, update_task, get_audit_logs, clear_audit_logs, init_db

# إعداد الصفحة
st.set_page_config(page_title="Project Sentinel", layout="wide", page_icon="🤖")

# --- نظام الحماية ---
def check_password():
    if st.session_state.get("password_correct", False): return True
    st.title("🔒 تسجيل الدخول - Project Sentinel")
    pwd = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if pwd == st.secrets.get("APP_PASS", "admin123"):
            st.session_state["password_correct"] = True; st.rerun()
        else: st.error("كلمة مرور خاطئة")
    return False

if not check_password(): st.stop()

# إعدادات قاعدة البيانات والذكاء الاصطناعي
db_config = {"host": st.secrets["DB_HOST"], "database": st.secrets["DB_NAME"], "user": st.secrets["DB_USER"], "password": st.secrets["DB_PASS"]}
init_db(db_config) 
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# تحميل البيانات
df_raw = get_all_tasks(db_config)

# الفلاتر الجانبية
st.sidebar.header("🔍 فلاتر")
status_filter = st.sidebar.multiselect("الحالة", options=df_raw['status'].unique() if not df_raw.empty else [], default=df_raw['status'].unique() if not df_raw.empty else [], key="f1")
df = df_raw[df_raw['status'].isin(status_filter)] if not df_raw.empty else df_raw

# التبويبات
tab1, tab2, tab3, tab4 = st.tabs(["📊 الداشبورد", "🤖 تقارير", "➕ إضافة مهام", "📜 سجل التغييرات"])

with tab1:
    st.metric("إجمالي المهام", len(df))
    st.dataframe(df, use_container_width=True)

with tab2:
    if st.button("توليد تقرير ذكي"):
        st.write(model.generate_content(f"حلل أداء المهام:\n{df.to_string()}").text)

with tab3:
    st.subheader("➕ إضافة مهمة جديدة")
    with st.form("add_task", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            proj = st.text_input("اسم المشروع")
            task = st.text_input("اسم المهمة")
            assigned = st.text_input("المسؤول")
        with col2:
            contact = st.text_input("رقم الهاتف (للواتساب)")
            status = st.selectbox("الحالة", ["Pending", "In Progress", "Done"])
            deadline = st.date_input("تاريخ التسليم")
        
        if st.form_submit_button("إضافة المهمة"):
            if proj and task and assigned:
                add_new_task(db_config, proj, task, assigned, contact, str(deadline), status)
                st.success("✅ تم إضافة المهمة بنجاح!")
                st.rerun()
            else:
                st.error("⚠️ يرجى ملء الحقول الأساسية")

with tab4:
    st.subheader("📜 سجل العمليات")
    if st.button("🗑️ مسح سجل التغييرات نهائياً"):
        clear_audit_logs(db_config)
        st.rerun()
    logs = get_audit_logs(db_config)
    st.dataframe(logs, use_container_width=True)