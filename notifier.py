import os
import pywhatkit as kit

def is_cloud_env():
    # التحقق إذا كنا بنشتغل على سيرفر (Streamlit Cloud)
    return "STREAMLIT_SERVER_PORT" in os.environ

def send_whatsapp_reminder(phone_number, text_message):
    if is_cloud_env():
        print("⚠️ إرسال الواتساب متاح فقط محلياً (Local).")
        return False
    
    try:
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        
        kit.sendwhatmsg_instantly(
            phone_no=phone_number,
            message=text_message,
            wait_time=15,
            tab_close=True
        )
        return True
    except Exception as e:
        print(f"خطأ أثناء إرسال رسالة الواتساب: {e}")
        return False