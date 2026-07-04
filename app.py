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
        st.subheader("1. التقرير العام")
        if st.button("توليد تقرير عام لكل المهام"):
            with st.spinner('جاري التحليل...'):
                try:
                    prompt = f"قم بتحليل بيانات المهام التالية واكتب تقريراً مختصراً عن سير العمل:\n{df.to_string()}"
                    response = model.generate_content(prompt)
                    st.write(response.text)
                except Exception as e:
                    st.error(f"خطأ اتصال بـ Gemini: {e}")
        
        st.divider() # خط فاصل
        
        # الجزء الثاني: تقرير مخصص لكل مهمة للواتساب
        st.subheader("2. إرسال تحديث عبر الواتساب")
        task_names = df['task_name'].tolist()
        selected_task = st.selectbox("اختر المهمة لإرسال تقريرها:", task_names)
        
        if st.button("تجهيز رسالة الواتساب"):
            with st.spinner('جاري صياغة الرسالة...'):
                # استخراج بيانات المهمة المحددة
                task_data = df[df['task_name'] == selected_task].iloc[0]
                phone = str(task_data.get('contact_info', '')).replace('+', '').strip()
                
                if phone and phone != 'None' and phone != 'nan':
                    try:
                        # طلب من جيميناي صياغة رسالة واتساب
                        prompt = f"""
                        اكتب رسالة واتساب قصيرة ومهنية باللغة العربية للموظف (المسند إليه: {task_data['assigned_to']}) 
                        لتحديثه بحالة المهمة التالية:
                        اسم المهمة: {task_data['task_name']}
                        الحالة: {task_data['status']}
                        تاريخ التسليم: {task_data['deadline']}
                        اجعل الرسالة ودية ومناسبة للعمل.
                        """
                        response = model.generate_content(prompt)
                        whatsapp_msg = response.text
                        
                        st.write("📝 **الرسالة المقترحة:**")
                        st.info(whatsapp_msg)
                        
                        # تحويل النص لصيغة يقبلها رابط الويب (URL Encoding)
                        encoded_msg = urllib.parse.quote(whatsapp_msg)
                        wa_link = f"https://wa.me/{phone}?text={encoded_msg}"
                        
                        # إنشاء زرار واتساب احترافي
                        st.markdown(
                            f"""
                            <a href="{wa_link}" target="_blank" 
                               style="background-color:#25D366; color:white; padding:10px 20px; 
                               text-decoration:none; border-radius:5px; font-weight:bold; display:inline-block; margin-top:10px;">
                               💬 إرسال التقرير عبر الواتساب
                            </a>
                            """, 
                            unsafe_allow_html=True
                        )
                    except Exception as e:
                        st.error(f"خطأ أثناء تجهيز الرسالة: {e}")
                else:
                    st.error("⚠️ لا يوجد رقم هاتف صالح مسجل لهذه المهمة. يرجى تعديل معلومات التواصل.")
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