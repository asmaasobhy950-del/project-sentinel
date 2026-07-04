import streamlit as st
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt
from agent_core import add_new_task, get_all_tasks

st.set_page_config(page_title="Project Sentinel", layout="wide")
st.title("🤖 Project Sentinel: لوحة تحكم الوكيل الذكي")

# 1. تهيئة Gemini و DB
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')
db_config = {
    "host": st.secrets['DB_HOST'], "database": st.secrets['DB_NAME'],
    "user": st.secrets['DB_USER'], "password": st.secrets['DB_PASS']
}

# جلب البيانات
df = get_all_tasks(db_config)

tab1, tab2, tab3 = st.tabs(["📊 الداشبورد", "🤖 تقارير Gemini", "➕ إضافة مهام"])

# --- التبويب 1: الداشبورد ---
with tab1:
    st.header("📊 حالة المهام")
    col1, col2 = st.columns([1, 2])
    
    # الرسم البياني
    with col1:
        st.subheader("توزيع الحالات")
        fig, ax = plt.subplots()
        df['status'].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%')
        st.pyplot(fig)
        
    # الجدول مع رابط الواتساب
    with col2:
        st.subheader("جدول المهام")
        df['واتساب'] = df.apply(lambda row: f"https://wa.me/{row['contact_info']}?text=تنبيه: مهمة {row['task_name']}", axis=1)
        st.dataframe(df)

# --- التبويب 2: تقرير Gemini ---
with tab2:
    st.header("🤖 التحليل الذكي")
    if st.button("توليد تقرير الأداء"):
        with st.spinner('جاري التحليل...'):
            try:
                response = model.generate_content(f"حلل أداء المهام دي وطلع تقرير:\n{df.to_string()}")
                st.write(response.text)
            except Exception as e:
                st.error(f"خطأ في الاتصال بـ Gemini: {e}")

# --- التبويب 3: إضافة المهام ---
with tab3:
    with st.form("new_task"):
        name = st.text_input("اسم المهمة")
        assigned = st.text_input("المسند إليه")
        contact = st.text_input("معلومات التواصل (بدون +)")
        status = st.selectbox("الحالة", ["Pending", "In Progress", "Done"])
        date = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة")

    if submit:
        try:
            add_new_task(db_config, name, assigned, contact, str(date), status)
            st.success("✅ تمت الإضافة!")
            st.rerun() # تحديث الصفحة فوراً
        except Exception as e: st.error(f"خطأ: {e}")