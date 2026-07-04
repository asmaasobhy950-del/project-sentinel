import streamlit as st
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt
import urllib.parse
# استدعاء الدوال الجديدة
from agent_core import add_new_task, get_all_tasks, delete_task, update_task

# --- إعداد الصفحة ---
st.set_page_config(page_title="Project Sentinel", layout="wide")
st.title("🤖 Project Sentinel: لوحة تحكم الوكيل الذكي")

# --- 1. تهيئة Gemini ---
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
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

# إنشاء التبويبات (أصبحوا 4 تبويبات)
tab1, tab2, tab3, tab4 = st.tabs(["📊 الداشبورد", "🤖 تقارير الفريق", "➕ إضافة مهام", "⚙️ إدارة المهام"])

# --- التبويب 1: الداشبورد ---
with tab1:
    st.header("📊 حالة المهام")
    if not df.empty:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("توزيع الحالات")
            fig, ax = plt.subplots()
            df['status'].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90)
            ax.set_ylabel('')
            st.pyplot(fig)
            
        with col2:
            st.subheader("جدول المهام")
            def generate_wa_link(row):
                contact = str(row.get('contact_info', ''))
                if contact == 'None' or contact.strip() == '':
                    return "لا يوجد رقم"
                clean_contact = contact.replace('+', '')
                return f"https://wa.me/{clean_contact}?text=تنبيه: بخصوص مهمة {row.get('task_name', '')}"
            
            df['واتساب'] = df.apply(generate_wa_link, axis=1)
            st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد بيانات لعرضها حالياً.")

# --- التبويب 2: تقارير Gemini ---
with tab2:
    st.header("🤖 التحليل الذكي ومراسلة الفريق")
    if not df.empty:
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
        
        st.subheader("☀️ 2. رسائل الصباح المجمعة للفريق")
        if st.button("تجهيز رسائل الصباح"):
            pending_tasks = df[df['status'] != 'Done']
            if not pending_tasks.empty:
                grouped_tasks = pending_tasks.groupby(['assigned_to', 'contact_info'])
                st.write("---")
                for (assigned, phone_num), person_tasks in grouped_tasks:
                    phone = str(phone_num).replace('+', '').strip()
                    if phone and phone != 'None' and phone != 'nan':
                        tasks_list_text = ""
                        for _, row in person_tasks.iterrows():
                            tasks_list_text += f"🔸 {row['task_name']} | ⏳ التسليم: {row['deadline']}\n"
                        
                        morning_msg = f"صباح الخير يا {assigned} ☀️\n\nدي قائمة بمهامك الحالية اللي محتاجة متابعة اليوم:\n\n{tasks_list_text}\nبالتوفيق في إنجازها! 🚀"
                        encoded_msg = urllib.parse.quote(morning_msg)
                        wa_link = f"https://wa.me/{phone}?text={encoded_msg}"
                        
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.markdown(f"**👤 {assigned}** (لديه {len(person_tasks)} مهام غير مكتملة)")
                        with col_b:
                            st.markdown(f'<a href="{wa_link}" target="_blank" style="background-color:#25D366; color:white; padding:8px 15px; text-decoration:none; border-radius:5px; font-weight:bold;">💬 إرسال التقرير</a>', unsafe_allow_html=True)
                        st.write("") 
                    else:
                        st.warning(f"⚠️ الموظف {assigned} ليس لديه رقم مسجل.")
            else:
                st.success("🎉 كل المهام الحالية مكتملة!")
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
        add_submit = st.form_submit_button("إضافة المهمة")

    if add_submit:
        if t_name and t_assigned:
            try:
                add_new_task(db_config, t_name, t_assigned, t_contact, str(t_date), t_status)
                st.success("✅ تمت الإضافة بنجاح!")
                st.rerun()
            except Exception as e:
                st.error(f"خطأ أثناء الإضافة: {e}")
        else:
            st.warning("رجاءً إدخال البيانات المطلوبة.")

# --- التبويب 4: تعديل وحذف المهام (الجديد) ---
with tab4:
    st.header("⚙️ تعديل أو حذف مهمة")
    if not df.empty:
        # اختيار المهمة المراد تعديلها أو حذفها
        task_names_list = df['task_name'].tolist()
        selected_task_name = st.selectbox("📌 اختر المهمة:", task_names_list)
        
        # جلب بيانات المهمة المختارة لملء الحقول تلقائياً
        task_data = df[df['task_name'] == selected_task_name].iloc[0]
        
        with st.form("edit_delete_form"):
            st.write(f"تعديل بيانات المهمة: **{selected_task_name}**")
            
            e_name = st.text_input("اسم المهمة", value=task_data['task_name'])
            e_assigned = st.text_input("المسند إليه", value=task_data['assigned_to'])
            
            # معالجة الرقم لو كان فارغ
            old_contact = str(task_data.get('contact_info', ''))
            if old_contact == 'None' or old_contact == 'nan': old_contact = ''
            e_contact = st.text_input("معلومات التواصل", value=old_contact)
            
            # تحديد الحالة الحالية
            status_options = ["Pending", "In Progress", "Done"]
            current_status = task_data['status']
            idx = status_options.index(current_status) if current_status in status_options else 0
            e_status = st.selectbox("الحالة", status_options, index=idx)
            
            # إدخال التاريخ كنص لتجنب تعقيدات تحويل التواريخ
            e_date = st.text_input("تاريخ التسليم (YYYY-MM-DD)", value=str(task_data['deadline']))
            
            st.markdown("---")
            col_update, col_delete = st.columns(2)
            with col_update:
                update_btn = st.form_submit_button("💾 حفظ التعديلات", use_container_width=True)
            with col_delete:
                # زر بلون مختلف للحذف
                delete_btn = st.form_submit_button("🗑️ حذف المهمة نهائياً", use_container_width=True)

        if update_btn:
            try:
                update_task(db_config, selected_task_name, e_name, e_assigned, e_contact, e_date, e_status)
                st.success("✅ تم تحديث بيانات المهمة بنجاح!")
                st.rerun()
            except Exception as e:
                st.error(f"خطأ أثناء التحديث: {e}")
                
        if delete_btn:
            try:
                delete_task(db_config, selected_task_name)
                st.success("🗑️ تم حذف المهمة بنجاح!")
                st.rerun()
            except Exception as e:
                st.error(f"خطأ أثناء الحذف: {e}")
    else:
        st.info("لا توجد مهام حالياً لإدارتها.")