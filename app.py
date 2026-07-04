import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px
import urllib.parse
from datetime import date
from agent_core import add_new_task, get_all_tasks, delete_task, update_task, get_audit_logs

# --- 1. تحسين واجهة الموبايل (PWA & Mobile CSS) ---
st.set_page_config(page_title="Sentinel Pro", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* تحسين شكل الأزرار على الموبايل */
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #f0f2f6; }
    /* جعل الجدول يستجيب للمس */
    .stDataFrame { border-radius: 15px; }
    /* إخفاء القوائم غير الضرورية في الموبايل */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# --- نظام الحماية ---
# ==========================================
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("🛡️ Sentinel Secure Access")
    pwd = st.text_input("أدخل كلمة مرور النظام", type="password")
    if st.button("دخول"):
        if pwd == st.secrets.get("APP_PASS", "admin123"):
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ كلمة مرور خاطئة")
    st.stop()

# --- جلب البيانات ---
db_config = {
    "host": st.secrets.get("DB_HOST"), "database": st.secrets.get("DB_NAME"),
    "user": st.secrets.get("DB_USER"), "password": st.secrets.get("DB_PASS")
}

@st.cache_data(ttl=30)
def load_all_data():
    df = get_all_tasks(db_config)
    # تحويل التاريخ لنوع datetime للمقارنة
    df['deadline'] = pd.to_datetime(df['deadline']).dt.date
    return df

df_raw = load_all_data()

# --- التنبيهات الذكية (Deadline Watchdog) ---
today = date.today()
overdue_df = df_raw[(df_raw['deadline'] < today) & (df_raw['status'] != 'Done')]

# --- الشريط الجانبي والفلاتر ---
st.sidebar.title(f"🗓️ {today}")
st.sidebar.divider()
employee_list = ["الكل"] + list(df_raw['assigned_to'].unique())
selected_emp = st.sidebar.selectbox("تصفية بالمسؤول:", employee_list)

df = df_raw if selected_emp == "الكل" else df_raw[df_raw['assigned_to'] == selected_emp]

# --- التبويبات ---
tabs = st.tabs(["📊 الإحصائيات", "🤖 التقارير والواتس", "⚙️ الإدارة", "📜 سجل التغييرات"])

# ==========================================
# --- التبويب 1: الداشبورد والتنبيهات ---
# ==========================================
with tabs[0]:
    # تنبيه المواعيد المتأخرة
    if not overdue_df.empty:
        st.error(f"⚠️ يوجد {len(overdue_df)} مهام متأخرة! يرجى المتابعة فوراً.")
        with st.expander("🔎 عرض المهام المتأخرة"):
            st.table(overdue_df[['task_name', 'assigned_to', 'deadline']])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("المهام", len(df))
    col2.metric("مكتملة", len(df[df['status']=='Done']))
    col3.metric("متأخرة", len(overdue_df), delta_color="inverse")
    
    # رسوم Plotly
    c_left, c_right = st.columns(2)
    with c_left:
        fig = px.sunburst(df, path=['status', 'assigned_to'], title="تحليل حالة المشروع")
        st.plotly_chart(fig, use_container_width=True)
    with c_right:
        fig2 = px.bar(df, x='deadline', color='status', title="الجدول الزمني للمهام")
        st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# --- التبويب 2: التقارير والواتس ---
# ==========================================
with tabs[1]:
    st.subheader("🤖 ذكاء الأعمال (Gemini)")
    if st.button("توليد تقرير الأداء العميق"):
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"حلل أداء الفريق، اذكر الموظفين الأكثر إنجازاً والمتأخرين:\n{df.to_string()}"
        st.write(model.generate_content(prompt).text)

    st.divider()
    st.subheader("💬 مراسلة الفريق")
    if st.button("🚀 تجهيز رسائل الصباح المجمعة"):
        for (name, phone), tasks in df[df['status']!='Done'].groupby(['assigned_to', 'contact_info']):
            msg = urllib.parse.quote(f"صباح الخير {name}، تذكير بمهامك اليوم:\n" + "\n".join([f"- {t}" for t in tasks['task_name']]))
            st.markdown(f"👤 **{name}** [👉 إرسال واتساب](https://wa.me/{str(phone).replace('+','')}/?text={msg})", unsafe_allow_html=True)

# ==========================================
# --- التبويب 3: الإدارة (CRUD) ---
# ==========================================
with tabs[2]:
    mode = st.radio("العملية:", ["إضافة مهمة", "تعديل/حذف مهمة"], horizontal=True)
    
    if mode == "إضافة مهمة":
        with st.form("add"):
            n = st.text_input("اسم المهمة")
            a = st.text_input("المسند إليه")
            p = st.text_input("رقم الهاتف")
            s = st.selectbox("الحالة", ["Pending", "In Progress", "Done"])
            d = st.date_input("التاريخ")
            if st.form_submit_button("حفظ") and n:
                add_new_task(db_config, n, a, p, str(d), s)
                st.cache_data.clear()
                st.success("تم الحفظ"); st.rerun()
    else:
        sel = st.selectbox("اختر مهمة:", df_raw['task_name'])
        curr = df_raw[df_raw['task_name']==sel].iloc[0]
        with st.form("edit"):
            en = st.text_input("الاسم", curr['task_name'])
            ea = st.text_input("المسؤول", curr['assigned_to'])
            es = st.selectbox("الحالة", ["Pending", "In Progress", "Done"], index=["Pending", "In Progress", "Done"].index(curr['status']))
            if st.form_submit_button("تحديث"):
                update_task(db_config, sel, en, ea, curr['contact_info'], str(curr['deadline']), es)
                st.cache_data.clear(); st.rerun()
            if st.form_submit_button("🗑️ حذف نهائي"):
                delete_task(db_config, sel)
                st.cache_data.clear(); st.rerun()

# ==========================================
# --- التبويب 4: سجل التغييرات (Audit) ---
# ==========================================
with tabs[3]:
    st.subheader("📜 سجل العمليات الأخير")
    logs = get_audit_logs(db_config)
    st.table(logs)