import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from agent_core import get_overdue_tasks, generate_ai_report, add_new_task, update_task_status
from notifier import send_whatsapp_reminder

# تحميل المتغيرات البيئية
load_dotenv()

st.set_page_config(page_title="Project Sentinel", layout="wide", page_icon="🤖")
st.title("🤖 Project Sentinel :لوحة تحكم الوكيل الذكي")

# إنشاء التبويبات الثلاثة
tab1, tab2, tab3 = st.tabs(["🔗 الإعدادات والربط", "📊 تشغيل الـ Agent", "➕ إدارة المهام والبيانات"])

# تجهيز الـ Session State تلقائياً من الـ .env
if 'db_config' not in st.session_state and os.getenv("DB_HOST"):
    st.session_state['db_config'] = {
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "sslmode": "require"
    }
    st.session_state['gemini_key'] = os.getenv("GEMINI_API_KEY")

# --- التبويب الأول: الإعدادات ---
with tab1:
    st.header("APIs إعدادات قاعدة البيانات والـ")
    db_host = st.text_input("Host", value=os.getenv("DB_HOST", ""))
    db_name = st.text_input("Database Name", value=os.getenv("DB_NAME", ""))
    db_user = st.text_input("User", value=os.getenv("DB_USER", ""))
    db_pass = st.text_input("Password", value=os.getenv("DB_PASS", ""), type="password")
    gemini_key = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
    
    if st.button("حفظ وتأكيد الإعدادات"):
        st.session_state['db_config'] = {"host": db_host, "database": db_name, "user": db_user, "password": db_pass, "sslmode": "require"}
        st.session_state['gemini_key'] = gemini_key
        st.success("✅ تم الحفظ وتفعيل الاتصال الآمن بنجاح!")

# --- التبويب الثاني: تشغيل الـ Agent ---
with tab2:
    if 'db_config' not in st.session_state:
        st.warning("⚠️ برجاء إدخال الإعدادات أولاً.")
    else:
        if st.button("🚀 فحص المشروعات وتشغيل الـ Agent"):
            with st.spinner("جاري فحص قاعدة البيانات وصياغة التقرير..."):
                try:
                    tasks = get_overdue_tasks(st.session_state['db_config'])
                    if tasks:
                        st.write("### 📋 المهام المتأخرة الحالية:")
                        import pandas as pd
                        df_display = pd.DataFrame(tasks)
                        st.dataframe(df_display)
                        st.session_state['current_tasks'] = tasks
                        
                        tasks_string = str(tasks)
                        report = generate_ai_report(tasks_string, st.session_state['gemini_key'])
                        st.write("### 🧠 التقرير الذكي المولد:")
                        st.info(report)
                        st.session_state['ai_report'] = report
                    else:
                        st.success("🎉 مفيش أي مهام متأخرة حالياً!")
                        if 'ai_report' in st.session_state: del st.session_state['ai_report']
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")

        if 'ai_report' in st.session_state and 'current_tasks' in st.session_state:
            st.write("---")
            if st.button("📱 إرسال تذكيرات الواتساب للفريق الآن"):
                with st.spinner("جاري الإرسال..."):
                    for task in st.session_state['current_tasks']:
                        name = task.get('assigned_to', 'المطور')
                        phone = task.get('contact_info', '')
                        task_name = task.get('task_name', '')
                        whatsapp_msg = f"أهلاً يا {name}، تذكير سريع بخصوص مهمة '{task_name}' المتأخرة. بالتوفيق!"
                        
                        if phone and not phone.startswith('+20110000'):
                            st.write(f"جاري الإرسال إلى {name}...")
                            if send_whatsapp_reminder(phone, whatsapp_msg):
                                st.success(f"✅ تم إرسال الرسالة لـ {name}!")
                        else:
                            st.warning(f"⚠️ تخطي {name} (الرقم وهمي).")

# --- التبويب الثالث: إدارة المهام والبيانات (CRUD) ---
with tab3:
    st.header("🛠️ التحكم المباشر في بيانات قاعدة البيانات")
    if 'db_config' not in st.session_state:
        st.warning("⚠️ يرجى ضبط الإعدادات أولاً.")
    else:
        col1, col2 = st.columns(2)
        
        # الجزء الأول: إضافة مهمة
        with col1:
            st.subheader("➕ إضافة مهمة جديدة")
            with st.form("add_task_form", clear_on_submit=True):
                new_title = st.text_input("اسم المهمة")
                new_owner = st.text_input("المسؤول عنها (الاسم)")
                new_phone = st.text_input("رقم الهاتف الدولي (مثل: 2010xxxxxxxx)")
                new_date = st.date_input("تاريخ التسليم (Deadline)")
                new_status = st.selectbox("الحالة الحالية", ["Pending", "In Progress", "Completed"])
                
                if st.form_submit_button("حفظ المهمة في قاعدة البيانات"):
                    if new_title and new_owner and new_phone:
                        if add_new_task(st.session_state['db_config'], new_title, new_owner, new_phone, str(new_date), new_status):
                            st.success("✅ تم إضافة المهمة بنجاح لقاعدة البيانات!")
                        else:
                            st.error("❌ حدث خطأ أثناء الإضافة.")
                    else:
                        st.warning("⚠️ برجاء ملء الحقول الأساسية.")
                    
        # الجزء الثاني: تعديل مهمة (تم ضبط المحاذاة تماماً هنا)
        with col2:
            st.subheader("🔄 تحديث حالة مهمة حركية")
            try:
                from agent_core import psycopg2
                conn = psycopg2.connect(**st.session_state['db_config'])
                cur = conn.cursor()
                cur.execute("SELECT task_name, assigned_to FROM tasks;")
                all_db_tasks = cur.fetchall()
                cur.close()
                conn.close()
                
                if all_db_tasks:
                    task_options = {f"{t[0]} ({t[1]})": t[0] for t in all_db_tasks}
                    selected_task_str = st.selectbox("اختار المهمة المراد تعديلها", list(task_options.keys()))
                    selected_task_name = task_options[selected_task_str]
                    
                    edit_status = st.selectbox("الحالة الجديدة", ["Pending", "In Progress", "Completed"], key="edit_status_key")
                    edit_phone = st.text_input("تعديل رقم الهاتف (اختياري)")
                    
                    if st.button("تحديث البيانات الآن"):
                        if update_task_status(st.session_state['db_config'], selected_task_name, edit_status, edit_phone if edit_phone else None):
                            st.success("✅ تم تحديث بيانات المهمة بنجاح!")
                            st.rerun()
                        else:
                            st.error("❌ فشل التحديث.")
                else:
                    st.info("لا يوجد مهام حالية في قاعدة البيانات للتعديل.")
            except Exception as e:
                st.error(f"خطأ أثناء قراءة المهام للتحرير: {e}")