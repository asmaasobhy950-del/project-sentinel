import os
from dotenv import load_dotenv
from agent_core import get_overdue_tasks, generate_ai_report
from notifier import send_whatsapp_reminder

def main():
    # 1. تحميل المتغيرات البيئية من ملف .env
    load_dotenv()
    
    db_config = {
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "sslmode": "require"
    }
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    print("🤖 جاري بدء فحص المشروع والمهام المتأخرة...")
    
    try:
        # 2. جلب المهام المتأخرة من قاعدة البيانات
        tasks = get_overdue_tasks(db_config)
        
        if tasks:
            print(f"📋 تم العثور على {len(tasks)} من المهام المتأخرة.")
            
            # 3. توليد التقرير الذكي عبر Gemini
            tasks_string = str(tasks)
            report = generate_ai_report(tasks_string, gemini_key)
            print("\n🧠 التقرير الذكي المولد:")
            print(report)
            print("-" * 50)
            
            # 4. إرسال التنبيهات تلقائياً عبر الواتساب للفريق
            print("📢 جاري إرسال التذكيرات التلقائية...")
            for task in tasks:
                name = task.get('assigned_to', 'المطور')
                phone = task.get('contact_info', '')
                task_name = task.get('task_name', '')
                
                whatsapp_msg = f"أهلاً يا {name}، تذكير سريع بخصوص مهمة '{task_name}' المتأخرة في المشروع. بالتوفيق!"
                
                # تخطي الأرقام الوهمية لمنع التعليق
                if phone and not phone.startswith('+20110000'):
                    print(f"📱 جاري الإرسال إلى {name} على الرقم ({phone})...")
                    success = send_whatsapp_reminder(phone, whatsapp_msg)
                    if success:
                        print(f"✅ تم الإرسال لـ {name} بنجاح.")
                else:
                    print(f"⚠️ تخطي {name} (الرقم وهمي أو غير مسجل).")
                    
            print("\n🎉 انتهت عملية الفحص والإرسال بنجاح!")
        else:
            print("🎉 ممتاز! مفيش أي مهام متأخرة حالياً في قاعدة البيانات.")
            
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع أثناء تشغيل الوكيل: {e}")

if __name__ == "__main__":
    main()