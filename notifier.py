import pywhatkit as kit
import time
import streamlit as st

def send_whatsapp_reminder(phone_number, text_message):
    """
    دالة لإرسال رسالة تذكيرية عبر الواتساب ويب تلقائياً
    """
    try:
        # التأكد إن الرقم بيبدأ بمفتاح الدولة (مثل +20)
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        
        # إرسال الرسالة فوراً (تفتح المتصفح وتبعت بعد 15 ثانية تلقائياً وتقفل التاب)
        # يمكنك تعديل وقت الانتظار إذا كان الإنترنت بطيئاً
        kit.sendwhatmsg_instantly(
            phone_no=phone_number,
            message=text_message,
            wait_time=15,
            tab_close=True
        )
        return True
    except Exception as e:
        st.error(f"خطأ أثناء إرسال رسالة الواتساب إلى {phone_number}: {e}")
        return False

def send_email_report(report_text, target_email):
    # دي دالة الإيميل هنسبها جاهزة لو حبيت تفعلها بعدين
    pass