import os

def send_whatsapp_reminder(phone_number, text_message):
    # التحقق من وجود شاشة (بيئة محلية)
    if "DISPLAY" not in os.environ:
        print("⚠️ إرسال الواتساب متاح فقط محلياً.")
        return False
    
    try:
        # الاستيراد هنا جوه الدالة بيخلي المكتبة متتحملش إلا عند الحاجة
        import pywhatkit as kit
        
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
        print(f"خطأ: {e}")
        return False