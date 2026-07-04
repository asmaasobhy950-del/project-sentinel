import streamlit as st
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt
from agent_core import add_new_task, get_all_tasks

# 1. إعدادات الصفحة
st.set_page_config(page_title="Project Sentinel", layout="wide")
st.title("🤖 Project Sentinel: لوحة تحكم الوكيل الذكي")

# 2. تهيئة الـ API والاتصال بقاعدة البيانات (معالجة الأخطاء)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # استخدام gemini-pro بدلاً من flash لتجنب خطأ 404
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.warning(f"⚠️ خطأ في إعداد Gemini: {e}")

# جلب الإعدادات بأمان
db_config = {
    "host": st.secrets.get("DB_HOST"),
    "database": st.secrets.get("DB_NAME"),
    "user": st.secrets.get("DB_USER"),
    "password": st.secrets.get("DB_PASS")
}

# 3. جلب البيانات
try:
    df = get_all_tasks(db_config)
except:
    df = pd.DataFrame()

# 4. التبويبات
tab1, tab2, tab3 = st.tabs(["📊 الداشبورد", "🤖 تقارير Gemini", "➕ إضافة مهام"])

# --- التبويب 1: الداشبورد ---
with tab1:
    st.header("📊 حالة المهام")
    if not df.empty:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("توزيع الحالات")
            fig, ax = plt.subplots()
            df['status'].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%')
            st.pyplot(fig)
        with col2:
            st.subheader("جدول المهام")
            # إضافة رابط الواتساب التلقائي
            df['واتساب'] = df.apply(lambda row: f"https://wa.me/{row['contact_info']}?text=تنبيه: مهمة {row['task_name']}", axis=1)
            st.dataframe(df)
    else:
        st.info("لا توجد بيانات حالياً.")

# --- التبويب 2: تقارير Gemini ---
with tab2:
    st.header("🤖 التحليل الذكي")
    if st.button("توليد تقرير الأداء"):
        if not df.empty:
            with st.spinner('جاري التحليل...'):
                try:
                    response = model.generate_content(f"قم بتحليل البيانات التالية وتقديم تقرير أداء مختصر:\n{df.to_string()}")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"خطأ في الاتصال بـ Gemini: {e}")
        else:
            st.warning("لا توجد بيانات للتحليل.")

# --- التبويب 3: إضافة المهام ---
with tab3:
    st.header("➕ إضافة مهمة جديدة")
    with st.form("new_task_form", clear_on_submit=True):
        task_name = st.text_input("اسم المهمة")
        assigned_to = st.text_input("المسند إليه")
        contact_info = st.text_input("معلومات التواصل (رقم الهاتف)")
        status = st.selectbox("الحالة", ["Pending", "In Progress", "Done"])
        deadline = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة المهمة")

    if submit:
        try:
            add_new_task(db_config, task_name, assigned_to, contact_info, str(deadline), status)
            st.success("✅ تمت الإضافة بنجاح!")
            st.rerun() # تحديث الصفحة
        except Exception as e:
            st.error(f"خطأ: {e}")