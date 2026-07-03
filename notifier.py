import os

def send_whatsapp_reminder(phone_number, text_message):
    # السطر ده بيمنع أي محاولة لفتح المتصفح لو إحنا على السيرفر
    if "STREAMLIT_SERVER_PORT" in os.environ:
        print("⚠️ إرسال الواتساب متاح فقط محلياً.")
        return False
    
    # الاستيراد لازم يكون هنا، جوه الدالة، مش بره
    import pywhatkit as kit
    
    try:
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        kit.sendwhatmsg_instantly(phone_no=phone_number, message=text_message, wait_time=15, tab_close=True)
        return True
    except Exception as e:
        print(f"خطأ: {e}")
        return False