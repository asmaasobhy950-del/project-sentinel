import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px
import urllib.parse
from agent_core import add_new_task, get_all_tasks, delete_task, update_task

# --- إعداد الصفحة ---
st.set_page_config(page_title="Project Sentinel", layout="wide", page_icon="🤖")

# ==========================================
# --- نظام الحماية (Authentication) ---
# ==========================================
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets.get("APP_PASS", "admin123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # أمان أكثر
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.title("🔒 تسجيل الدخول - Project Sentinel")
    st.text_input("أدخل كلمة المرور للنظام", type="password", on_change=password_entered, key="password")
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("كلمة المرور غير صحيحة!")
    return False

# إيقاف تنفيذ باقي الكود إذا لم يتم تسجيل الدخول
if not check_password():
    st.stop()

# ==========================================
# --- الإعدادات الأساسية بعد تسجيل الدخول ---
# ==========================================
st.title("🤖 Project Sentinel: لوحة تحكم الوكيل الذكي")

try:
    genai.configure(api_key=st.secrets.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"خطأ في تهيئة Gemini: {e}")

db_config = {
    "host": st.secrets.get("DB_HOST"),
    "database": st.secrets.get("DB_NAME"),
    "user": st.secrets.get("DB_USER"),
    "password": st.secrets.get("DB_PASS")
}

@st.cache_data(ttl=60)
def load_data():
    try:
        return get_all_tasks(db_config)
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {e}")
        return pd.DataFrame()

df_raw = load_data()

# ==========================================
# --- الفلاتر الجانبية (Sidebar Filters) ---
# ==========================================
st.sidebar.header("🔍 فلاتر البيانات")
if not df_raw.empty:
    # فلتر الحالة
    status_filter = st.sidebar.multiselect(
        "تصفية حسب الحالة:",
        options=df_raw['status'].unique(),
        default=df_raw['status'].unique()
    )
    # فلتر الموظف
    employee_filter = st.sidebar.multiselect(
        "تصفية حسب الموظف:",
        options=df_raw['assigned_to'].unique(),
        default=df_raw['assigned_to'].unique()
    )
    
    # تطبيق الفلاتر
    df = df_raw[(df_raw['status'].isin(status_filter)) & (df_raw['assigned_to'].isin(employee_filter))]
else:
    df = df_raw

# إنشاء التبويبات
tab1, tab2, tab3, tab4 = st.tabs(["📊 الداشبورد", "🤖 تقارير الفريق", "➕ إضافة مهام", "⚙️ إدارة المهام"])

# ==========================================
# --- التبويب 1: الداشبورد ---
# ==========================================
with tab1:
    if not df.empty:
        # تصدير البيانات (Exporting Capabilities)
        col_title, col_export = st.columns([4, 1])
        with col_export:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 تحميل التقرير (CSV)",
                data=csv,
                file_name='sentinel_tasks.csv',
                mime='text/csv',
                use_container_width=True
            )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي المهام", len(df))
        c2.metric("✅ مكتملة", len(df[df['status'] == 'Done']))
        c3.metric("⏳ قيد التنفيذ", len(df[df['status'] == 'In Progress']))
        c4.metric("🛑 معلقة", len(df[df['status'] == 'Pending']))
        
        st.divider()
        
        col_chart1, col_chart2 = st.columns(2)
        color_map = {'Done': '#2ecc71', 'In Progress': '#f1c40f', 'Pending': '#e74c3c'}
        
        with col_chart1:
            fig_pie = px.pie(df, names='status', hole=0.4, color='status', color_discrete_map=color_map)
            fig_pie.update_layout(title="توزيع الحالات")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_chart2:
            fig_bar = px.histogram(df, x='assigned_to', color='status', color_discrete_map=color_map)
            fig_bar.update_layout(barmode='stack', title="حمل العمل لكل موظف")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        def generate_wa_link(row):
            contact = str(row.get('contact_info', ''))
            if contact == 'None' or not contact.strip(): return "لا يوجد رقم"
            return f"https://wa.me/{contact.replace('+', '')}?text=تنبيه: بخصوص مهمة {row.get('task_name', '')}"
        
        df_display = df.copy()
        df_display['واتساب'] = df_display.apply(generate_wa_link, axis=1)
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("لا توجد بيانات تطابق الفلاتر المحددة.")

# ==========================================
# --- التبويب 2: تقارير Gemini ---
# ==========================================
with tab2:
    if not df.empty:
        if st.button("توليد تقرير للإدارة"):
            with st.spinner('جاري التحليل...'):
                try:
                    response = model.generate_content(f"حلل بيانات المهام:\n{df.to_string()}")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"خطأ اتصال بـ Gemini: {e}")
        
        st.divider()
        st.subheader("☀️ رسائل الصباح المجمعة للفريق")
        
        if st.button("تجهيز رسائل الصباح"):
            pending_tasks = df[df['status'] != 'Done']
            if not pending_tasks.empty:
                for (assigned, phone_num), person_tasks in pending_tasks.groupby(['assigned_to', 'contact_info']):
                    phone = str(phone_num).replace('+', '').strip()
                    if phone and phone != 'None':
                        tasks_list = "\n".join([f"🔸 {r['task_name']} | التسليم: {r['deadline']}" for _, r in person_tasks.iterrows()])
                        msg = urllib.parse.quote(f"صباح الخير {assigned} ☀️\nمهامك اليوم:\n{tasks_list}")
                        
                        col_a, col_b = st.columns([3, 1])
                        col_a.markdown(f"**👤 {assigned}**")
                        col_b.markdown(f'<a href="https://wa.me/{phone}?text={msg}" target="_blank" style="background-color:#25D366; color:white; padding:8px; border-radius:5px; text-decoration:none;">💬 إرسال</a>', unsafe_allow_html=True)
            else:
                st.success("المهام مكتملة!")

# ==========================================
# --- التبويب 3 و 4: الإضافة، التعديل، الحذف ---
# ==========================================
with tab3:
with st.form("new_task_form", clear_on_submit=True):
        t_company = st.text_input("اسم الشركة")
        t_project = st.text_input("اسم المشروع")
        t_name = st.text_input("اسم المهمة")
        t_assigned = st.text_input("المسند إليه")
        t_contact = st.text_input("رقم التليفون")
        t_status = st.selectbox("الحالة", ["Pending", "In Progress", "Done"])
        t_date = st.date_input("تاريخ التسليم")
        
        if st.form_submit_button("إضافة"):
            add_new_task(db_config, t_name, t_assigned, t_contact, str(t_date), t_status, t_company, t_project)
            st.success("تمت الإضافة!")
            st.rerun()

with tab4:
    if not df_raw.empty:
        selected_task = st.selectbox("📌 اختر المهمة:", df_raw['task_name'].tolist())
        t_data = df_raw[df_raw['task_name'] == selected_task].iloc[0]
        
        with st.form("edit_form"):
            e_name = st.text_input("اسم المهمة", value=t_data['task_name'])
            e_assigned = st.text_input("المسند إليه", value=t_data['assigned_to'])
            e_contact = st.text_input("رقم التليفون", value=str(t_data.get('contact_info', '')))
            e_status = st.selectbox("الحالة", ["Pending", "In Progress", "Done"], index=["Pending", "In Progress", "Done"].index(t_data['status']))
            e_date = st.text_input("تاريخ التسليم", value=str(t_data['deadline']))
            
            c_upd, c_del = st.columns(2)
            if c_upd.form_submit_button("💾 حفظ التعديلات"):
                update_task(db_config, selected_task, e_name, e_assigned, e_contact, e_date, e_status)
                st.cache_data.clear()
                st.rerun()
            if c_del.form_submit_button("🗑️ حذف المهمة"):
                delete_task(db_config, selected_task)
                st.cache_data.clear()
                st.rerun()