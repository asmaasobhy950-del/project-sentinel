import streamlit as st
import pandas as pd
import google.generativeai as genai
from agent_core import get_all_tasks, add_new_task

# إعداد Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Sentinel Dashboard", layout="wide")
tab1, tab2, tab3 = st.tabs(["📊 الداشبورد", "🤖 تقارير Gemini", "➕ إضافة مهام"])

# جلب البيانات
tasks_df = get_all_tasks(st.session_state['db_config'])

with tab1:
    st.header("إحصائيات المهام")
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المهام", len(tasks_df))
    col2.metric("مهام قيد التنفيذ", len(tasks_df[tasks_df['status'] == 'In Progress']))
    st.dataframe(tasks_df) # عرض كل البيانات بالـ status والكونتكت

with tab2:
    st.header("التحليل الذكي للمهام")
    if st.button("توليد تقرير ذكي"):
        prompt = f"حلل هذه المهام واكتب تقرير أداء: {tasks_df.to_string()}"
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        st.write(response.text)

with tab3:
    st.header("إضافة مهمة مع كافة التفاصيل")
    with st.form("new_task"):
        # إضافة حقول جديدة
        status = st.selectbox("الحالة", ["Pending", "In Progress", "Done"])
        contact = st.text_input("معلومات التواصل")
        # ... باقي الحقول (الاسم، الشخص، التاريخ)
        if st.form_submit_button("إضافة"):
            # استدعاء الدالة مع الـ status والـ contact
            add_new_task(..., status, contact)