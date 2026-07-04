import streamlit as st
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt
from agent_core import add_new_task, get_all_tasks

st.set_page_config(page_title="Project Sentinel", layout="wide")
st.title("🤖 Project Sentinel: لوحة تحكم الوكيل الذكي")

# 1. تهيئة Gemini بشكل أكثر قوة
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    # استخدام الموديل الأكثر استقراراً حالياً
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"خطأ في تهيئة Gemini: {e}")

# جلب البيانات
db_config = {
    "host": st.secrets.get("DB_HOST"), "database": st.secrets.get("DB_NAME"),
    "user": st.secrets.get("DB_USER"), "password": st.secrets.get("DB_PASS")
}

try:
    df = get_all_tasks(db_config)
except:
    df = pd.DataFrame()

# 2. التبويبات
tab1, tab2, tab3 = st.tabs(["📊 الداشبورد", "🤖 تقارير Gemini", "➕ إضافة مهام"])

with tab1:
    st.header("📊 حالة المهام")
    if not df.empty:
        col1, col2 = st.columns([1, 2])
        with col1:
            fig, ax = plt.subplots()
            df['status'].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%')
            st.pyplot(fig)
        with col2:
            st.dataframe(df)
    else:
        st.info("لا توجد بيانات.")

with tab2:
    st.header("🤖 التحليل الذكي")
    if st.button("توليد تقرير الأداء"):
        if not df.empty:
            with st.spinner('جاري التحليل عبر Gemini...'):
                try:
                    # تعديل طريقة الطلب لضمان التوافق
                    response = model.generate_content(f"قم بتحليل البيانات التالية وتقديم تقرير أداء مختصر:\n{df.to_string()}")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"خطأ اتصال Gemini: {e}. يرجى التأكد من أن الـ API Key مفعل.")
        else:
            st.warning("لا توجد بيانات للتحليل.")

with tab3:
    with st.form("new_task_form", clear_on_submit=True):
        task_name = st.text_input("اسم المهمة")
        assigned_to = st.text_input("المسند إليه")
        contact_info = st.text_input("معلومات التواصل")
        status = st.selectbox("الحالة", ["Pending", "In Progress", "Done"])
        deadline = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة المهمة")

    if submit:
        try:
            add_new_task(db_config, task_name, assigned_to, contact_info, str(deadline), status)
            st.success("✅ تمت الإضافة!")
            st.rerun()
        except Exception as e:
            st.error(f"خطأ: {e}")