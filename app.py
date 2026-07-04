import streamlit as st
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt
from agent_core import add_new_task, get_all_tasks
import urllib.parse

# --- إعداد الصفحة ---
st.set_page_config(page_title="Project Sentinel", layout="wide")
st.title("🤖 Project Sentinel: لوحة تحكم الوكيل الذكي")

# --- 1. تهيئة Gemini ---
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    # التحديث للإصدار المطلوب
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"خطأ في تهيئة Gemini: {e}")

# --- 2. إعداد قاعدة البيانات بأمان ---
db_config = {
    "host": st.secrets.get("DB_HOST"),
    "database": st.secrets.get("DB_NAME"),
    "user": st.secrets.get("DB_USER"),
    "password": st.secrets.get("DB_PASS")
}

# --- 3. جلب البيانات ---
try:
    df = get_all_tasks(db_config)
except Exception as e:
    df = pd.DataFrame()
    st.error(f"خطأ في جلب البيانات: {e}")

# إنشاء التبويبات
tab1, tab2, tab3 = st.tabs(["📊 الداشبورد", "🤖 تقارير Gemini", "➕ إضافة مهام"])

# --- التبويب 1: الداشبورد ---
with tab1:
    st.header("📊 حالة المهام")
    if not df.empty:
        col1, col2 = st.columns([1, 2])
        
        # الرسم البياني
        with col1:
            st.subheader("توزيع الحالات")
            fig, ax = plt.subplots()
            df['status'].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90)
            ax.set_ylabel('') # لتنظيف شكل الرسمة
            st.pyplot(fig)
            
        # جدول البيانات ورابط الواتس
        with col2:
            st.subheader("جدول المهام")
            
            # دالة لتوليد رابط الواتس وتجنب أخطاء الأرقام الفارغة (NULL)
            def generate_wa_link(row):
                contact = str(row.get('contact_info', ''))
                if contact == 'None' or contact.strip() == '':
                    return "لا يوجد رقم"
                # إزالة علامة + إذا كانت موجودة ليعمل الرابط بشكل صحيح
                clean_contact = contact.replace('+', '')
                return f"https://wa.me/{clean_contact}?text=تنبيه: بخصوص مهمة {row.get('task_name', '')}"
            
            df['واتساب'] = df.apply(generate_wa_link, axis=1)
            st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد بيانات لعرضها حالياً.")

# --- التبويب 2: تقارير Gemini وربط الواتساب ---
with tab2:
    st.header("🤖 التحليل الذكي ومراسلة الفريق")
    
    if not df.empty:
        # الجزء الأول: تقرير عام للمشروع
        st.subheader("1. التقرير العام للإدارة")
        if st.button("توليد تقرير عام لكل المهام"):
            with st.spinner('جاري التحليل...'):
                try:
                    prompt = f"قم بتحليل بيانات المهام التالية واكتب تقريراً مختصراً عن سير العمل:\n{df.to_string()}"
                    response = model.generate_content(prompt)
                    st.write(response.text)
                except Exception as e:
                    st.error(f"خطأ اتصال بـ Gemini: {e}")
        
        st.divider()
        
        # الجزء الثاني: التقرير الصباحي المجمع (تحديث يومي للموظفين)
        st.subheader("☀️ 2. رسائل الصباح المجمعة للفريق")
        st.write("اضغطي على الزر لتجميع المهام (غير المكتملة) لكل موظف وتجهيز رسائل الواتساب.")
        
        if st.button("تجهيز رسائل الصباح"):
            # استبعاد المهام المكتملة (Done) عشان منبعتهاش كل يوم
            pending_tasks = df[df['status'] != 'Done']
            
            if not pending_tasks.empty:
                # تجميع البيانات حسب الموظف ورقم التليفون
                grouped_tasks = pending_tasks.groupby(['assigned_to', 'contact_info'])
                
                st.write("---")
                # المرور على كل موظف وتجهيز رسالته
                for (assigned, phone_num), person_tasks in grouped_tasks:
                    phone = str(phone_num).replace('+', '').strip()
                    
                    if phone and phone != 'None' and phone != 'nan':
                        # تجميع المهام في نص واحد
                        tasks_list_text = ""
                        for _, row in person_tasks.iterrows():
                            tasks_list_text += f"🔸 {row['task_name']} | ⏳ التسليم: {row['deadline']}\n"
                        
                        # صياغة الرسالة الصباحية
                        morning_msg = f"صباح الخير يا {assigned} ☀️\n\nدي قائمة بمهامك الحالية اللي محتاجة متابعة اليوم:\n\n{tasks_list_text}\nبالتوفيق في إنجازها! 🚀"
                        
                        # تشفير الرابط
                        encoded_msg = urllib.parse.quote(morning_msg)
                        wa_link = f"https://wa.me/{phone}?text={encoded_msg}"
                        
                        # عرض الموظف وزر الإرسال الخاص به
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.markdown(f"**👤 {assigned}** (لديه {len(person_tasks)} مهام غير مكتملة)")
                        with col_b:
                            st.markdown(
                                f"""
                                <a href="{wa_link}" target="_blank" 
                                   style="background-color:#25D366; color:white; padding:8px 15px; 
                                   text-decoration:none; border-radius:5px; font-size:14px; font-weight:bold; display:inline-block;">
                                   💬 إرسال للموظف
                                </a>
                                """, 
                                unsafe_allow_html=True
                            )
                        st.write("") # مسافة صغيرة بين كل موظف والتاني
                    else:
                        st.warning(f"⚠️ الموظف {assigned} ليس لديه رقم هاتف مسجل.")
            else:
                st.success("🎉 كل المهام الحالية مكتملة (Done)! لا يوجد رسائل صباحية اليوم.")
    else:
        st.warning("لا توجد بيانات لتحليلها.")
# --- التبويب 3: إضافة المهام ---
with tab3:
    st.header("➕ إضافة مهمة جديدة")
    with st.form("new_task_form", clear_on_submit=True):
        t_name = st.text_input("اسم المهمة")
        t_assigned = st.text_input("المسند إليه")
        t_contact = st.text_input("معلومات التواصل (رقم التليفون)")
        t_status = st.selectbox("الحالة", ["Pending", "In Progress", "Done"])
        t_date = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة المهمة")

    if submit:
        if t_name and t_assigned:
            try:
                add_new_task(db_config, t_name, t_assigned, t_contact, str(t_date), t_status)
                st.success("✅ تمت الإضافة بنجاح!")
                st.rerun() # تحديث فوري للصفحة
            except Exception as e:
                st.error(f"خطأ أثناء الإضافة: {e}")
        else:
            st.warning("رجاءً إدخال اسم المهمة والمسند إليه على الأقل.")