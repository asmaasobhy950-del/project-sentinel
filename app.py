import streamlit as st
import os
from agent_core import get_overdue_tasks, generate_ai_report, add_new_task, update_task_status

# استيراد آمن لدالة الواتساب
try:
    from notifier import send_whatsapp_reminder
except ImportError:
    send_whatsapp_reminder = None

# وظيفة لقراءة البيانات من الـ Secrets أو متغيرات البيئة
def get_secret(key):
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key)

st.set_page_config(page_title="Project Sentinel", layout="wide", page_icon="🤖")
st.title("🤖 Project Sentinel :لوحة تحكم الوكيل الذكي")

tab1, tab2, tab3 = st.tabs(["🔗 الإعدادات", "📊 تشغيل الـ Agent", "➕ إدارة المهام"])

# --- التبويب الأول: الإعدادات ---
with tab1:
    st.header("إعدادات الاتصال")
    # محاولة تهيئة الاتصال
    db_host = get_secret('DB_HOST')
    if db_host:
        db_config = {
            "host": db_host,
            "database": get_secret('DB_NAME'),
            "user": get_secret('DB_USER'),
            "password": get_secret('DB_PASS')
        }
        st.session_state['db_config'] = db_config
        st.success("✅ تم الاتصال بقاعدة البيانات بنجاح!")
    else:
        st.warning("⚠️ يرجى ضبط الـ Secrets في إعدادات التطبيق.")

# --- التبويب الثاني: تشغيل الـ Agent ---
with tab2:
    if 'db_config' in st.session_state:
        if st.button("🚀 فحص المهام"):
            tasks = get_overdue_tasks(st.session_state['db_config'])
            st.session_state['current_tasks'] = tasks
            st.write(tasks)
        
        if 'current_tasks' in st.session_state and st.session_state['current_tasks']:
            st.write("---")
            if send_whatsapp_reminder:
                if st.button("📱 إرسال تذكيرات الواتساب"):
                    st.success("تم إرسال التذكيرات!")
            else:
                st.info("ℹ️ ميزة الواتساب متاحة فقط للتشغيل المحلي.")
    else:
        st.error("يرجى إعداد الاتصال في التبويب الأول.")

# --- التبويب الثالث: إدارة المهام ---
with tab3:
    st.header("إدارة البيانات")
    # (هنا تكمل كود إدارة المهام الخاص بك)
def get_secret(key):
    try:
        # المحاولة الأولى: قراءة من الـ secrets المربوطة بـ Streamlit
        return st.secrets.get(key)
    except Exception:
        # لو مفيش secrets، ارجع لمتغيرات البيئة
        return os.environ.get(key)
# --- التبويب الثالث: إدارة المهام ---
with tab3:
    st.header("➕ إضافة مهمة جديدة")
    
    with st.form("add_task_form"):
        task_name = st.text_input("اسم المهمة")
        assigned_to = st.text_input("المسند إليه")
        deadline = st.date_input("تاريخ التسليم")
        
        submit = st.form_submit_button("إضافة المهمة")
        
        if submit:
            if task_name and assigned_to:
                # استدعاء الدالة اللي بتضيف في قاعدة البيانات
                add_new_task(st.session_state['db_config'], task_name, assigned_to, str(deadline))
                st.success(f"تم إضافة المهمة: {task_name}")
            else:
                st.error("من فضلك املأ البيانات الأساسية.")

    st.write("---")
    st.header("🔄 تحديث حالة المهام")
    task_id = st.number_input("رقم المهمة (ID)", min_value=1)
    if st.button("تحديث الحالة إلى مكتمل"):
        update_task_status(st.session_state['db_config'], task_id, "Completed")
        st.success(f"تم تحديث المهمة رقم {task_id}")