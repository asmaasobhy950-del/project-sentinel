import streamlit as st
import pandas as pd
import google.generativeai as genai
from agent_core import add_new_task, get_all_tasks

st.set_page_config(page_title="Project Sentinel", layout="wide")
st.title("🤖 Project Sentinel: لوحة تحكم الوكيل الذكي")

# تهيئة الـ API Key لـ Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash') # موديل أحدث وأسرع

# تبويبات المشروع
tab1, tab2, tab3 = st.tabs(["📊 الداشبورد", "🤖 تقارير Gemini", "➕ إضافة مهام"])

# جلب البيانات (مرة واحدة)
db_config = {
    "host": st.secrets['DB_HOST'], "database": st.secrets['DB_NAME'],
    "user": st.secrets['DB_USER'], "password": st.secrets['DB_PASS']
}
df = get_all_tasks(db_config)

# --- التبويب 1: الداشبورد ---
with tab1:
    st.header("📊 حالة المهام")
    col1, col2 = st.columns([1, 2])
    with col1:
        status_counts = df['status'].value_counts()
        st.bar_chart(status_counts) # رسم بياني للحالة
    with col2:
        st.dataframe(df)

# --- التبويب 2: Gemini ---
with tab2:
    st.header("🤖 التحليل الذكي")
    if st.button("توليد تقرير أداء"):
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
        contact = st.text_input("معلومات التواصل")
        status = st.selectbox("الحالة", ["Pending", "In Progress", "Done"])
        date = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة")

    if submit:
        add_new_task(db_config, name, assigned, contact, str(date), status)
        st.success("✅ تمت الإضافة!")
    # داخل التبويب الأول (الداشبورد)
with tab1:
    st.header("📊 حالة المهام")
    # ... الكود السابق ...
    
    # دالة بسيطة لإنشاء رابط الواتساب
    def get_whatsapp_link(phone, task_name):
        base_url = "https://wa.me/"
        message = f"تنبيه بخصوص مهمة: {task_name}"
        return f"{base_url}{phone}?text={message}"

    # إضافة عمود روابط الواتساب للجدول
    df['واتساب'] = df.apply(lambda row: get_whatsapp_link(row['contact_info'], row['task_name']), axis=1)
    
    # عرض الجدول مع الروابط (Streamlit هيعرضهم كروابط قابلة للضغط)
    st.dataframe(df)