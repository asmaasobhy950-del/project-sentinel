import streamlit as st
import os
from dotenv import load_dotenv
from agent_core import get_overdue_tasks, generate_ai_report, add_new_task, update_task_status

# استيراد آمن للدالة (في حال كانت السحابة لا تدعم pywhatkit)
try:
    from notifier import send_whatsapp_reminder
except ImportError:
    send_whatsapp_reminder = None

load_dotenv()
# (باقي كود الإعدادات كما هو...)
# ... عند زرار الإرسال في التبويب الثاني ...

if 'ai_report' in st.session_state and 'current_tasks' in st.session_state:
    st.write("---")
    if send_whatsapp_reminder:
        if st.button("📱 إرسال تذكيرات الواتساب للفريق الآن"):
            with st.spinner("جاري الإرسال..."):
                for task in st.session_state['current_tasks']:
                    # ... (نفس كود الإرسال السابق) ...
                    pass
    else:
        st.info("ℹ️ إرسال الواتساب متاح فقط عند تشغيل التطبيق محلياً على جهازك.")