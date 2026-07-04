import streamlit as st
from agent_core import add_new_task, get_all_tasks

# 1. إعدادات الصفحة
st.set_page_config(page_title="Project Sentinel", layout="wide", page_icon="🤖")
st.title("🤖 Project Sentinel: لوحة تحكم الوكيل الذكي")

# 2. تهيئة الاتصال بقاعدة البيانات بشكل آمن
if 'db_config' not in st.session_state:
    try:
        st.session_state['db_config'] = {
            "host": st.secrets['DB_HOST'],
            "database": st.secrets['DB_NAME'],
            "user": st.secrets['DB_USER'],
            "password": st.secrets['DB_PASS']
        }
    except Exception:
        st.session_state['db_config'] = None

# 3. التبويبات
tab1, tab2, tab3 = st.tabs(["📊 الداشبورد", "🤖 تقارير Gemini", "➕ إضافة مهام"])

# --- التبويب 1: الداشبورد ---
with tab1:
    st.header("📊 عرض قاعدة البيانات")
    if st.session_state.get('db_config'):
        try:
            tasks_df = get_all_tasks(st.session_state['db_config'])
            st.dataframe(tasks_df) # عرض البيانات
        except Exception as e:
            st.error(f"خطأ في جلب البيانات: {e}")
    else:
        st.error("لم يتم الاتصال بقاعدة البيانات.")

# --- التبويب 3: إضافة مهام (الاستدعاء الآمن) ---
with tab3:
    st.header("➕ إضافة مهمة جديدة")
    with st.form("new_task_form", clear_on_submit=True):
        task_name = st.text_input("اسم المهمة")
        assigned_to = st.text_input("المسند إليه")
        contact_info = st.text_input("معلومات التواصل")
        status = st.selectbox("الحالة", ["Pending", "In Progress", "Done"])
        deadline = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة")

    # الاستدعاء الصحيح: داخل الشرط فقط
    if submit:
        config = st.session_state.get('db_config')
        if config and task_name and assigned_to:
            try:
                add_new_task(config, task_name, assigned_to, str(deadline), status, contact_info)
                st.success("✅ تمت إضافة المهمة!")
            except Exception as e:
                st.error(f"خطأ: {e}")
        else:
            st.warning("⚠️ يرجى ملء كافة البيانات.")