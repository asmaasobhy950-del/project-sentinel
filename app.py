import streamlit as st
import pandas as pd
import google.generativeai as genai
from agent_core import add_new_task, get_all_tasks

st.set_page_config(page_title="Project Sentinel", layout="wide", page_icon="🤖")
st.title("🤖 Project Sentinel: لوحة تحكم الوكيل الذكي")

# تهيئة الاتصال الآمن
if 'db_config' not in st.session_state:
    try:
        st.session_state['db_config'] = {
            "host": st.secrets['DB_HOST'], "database": st.secrets['DB_NAME'],
            "user": st.secrets['DB_USER'], "password": st.secrets['DB_PASS']
        }
    except: st.session_state['db_config'] = None

# إعداد Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

tab1, tab2, tab3 = st.tabs(["📊 الداشبورد", "🤖 تقارير Gemini", "➕ إضافة مهام"])

# --- التبويب 1: الداشبورد ---
with tab1:
    st.header("📊 حالة المهام")
    if st.session_state.get('db_config'):
        df = get_all_tasks(st.session_state['db_config'])
        st.dataframe(df) # عرض الجدول
        # إحصائيات بسيطة
        st.metric("إجمالي المهام", len(df))
    else: st.error("فشل الاتصال بقاعدة البيانات.")

# --- التبويب 2: Gemini ---
with tab2:
    st.header("🤖 التحليل الذكي")
    if st.button("توليد تقرير الأداء"):
        df = get_all_tasks(st.session_state['db_config'])
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"حلل أداء المهام التالية: {df.to_string()}")
        st.write(response.text)

# --- التبويب 3: إضافة المهام ---
with tab3:
    with st.form("new_task"):
        name = st.text_input("اسم المهمة")
        assigned = st.text_input("المسند إليه")
        contact = st.text_input("معلومات التواصل")
        status = st.selectbox("الحالة", ["Pending", "In Progress", "Done"])
        date = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة")

    if submit:
        try:
            add_new_task(st.session_state['db_config'], name, assigned, contact, str(date), status)
            st.success("✅ تمت الإضافة!")
        except Exception as e: st.error(f"خطأ: {e}")