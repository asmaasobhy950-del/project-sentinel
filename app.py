import streamlit as st
from agent_core import add_new_task, get_overdue_tasks

st.set_page_config(page_title="Project Sentinel", layout="wide")
st.title("🤖 Project Sentinel")

# تهيئة الاتصال
if 'db_config' not in st.session_state:
    try:
        st.session_state['db_config'] = {
            "host": st.secrets['DB_HOST'],
            "database": st.secrets['DB_NAME'],
            "user": st.secrets['DB_USER'],
            "password": st.secrets['DB_PASS']
        }
    except:
        st.session_state['db_config'] = None

# تعريف التبويبات مرة واحدة في بداية الصفحة
tab1, tab2, tab3 = st.tabs(["🔗 الإعدادات", "📊 تشغيل الـ Agent", "➕ إدارة المهام"])

# --- التبويب الأول ---
with tab1:
    st.header("إعدادات الاتصال")
    if st.session_state.get('db_config'):
        st.success("✅ متصل بقاعدة البيانات بنجاح!")
    else:
        st.error("❌ فشل الاتصال.")

# --- التبويب الثاني: تشغيل الـ Agent ---
with tab2:
    st.header("📊 تشغيل الـ Agent")
    
    # إضافة زرار للتحديث
    if st.button("🚀 فحص المهام المحدثة"):
        # مسح الذاكرة المؤقتة لضمان جلب بيانات جديدة
        st.cache_data.clear() 
        
        config = st.session_state.get('db_config')
        if config:
            # استدعاء الدالة لجلب البيانات
            tasks = get_overdue_tasks(config)
            
            if tasks:
                st.write(tasks)
            else:
                st.info("لا توجد مهام متأخرة حالياً.")
        else:
            st.error("لا يوجد اتصال بقاعدة البيانات.")

# --- التبويب الثالث ---
with tab3:
    st.header("➕ إضافة مهمة جديدة")
    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input("اسم المهمة")
        assigned_to = st.text_input("المسند إليه")
        deadline = st.date_input("تاريخ التسليم")
        submit = st.form_submit_button("إضافة المهمة")

    if submit:
        config = st.session_state.get('db_config')
        if config and task_name and assigned_to:
            try:
                add_new_task(config, task_name, assigned_to, str(deadline), "In Progress")
                st.success("✅ تمت إضافة المهمة بنجاح!")
            except Exception as e:
                st.error(f"خطأ: {e}")
        else:
            st.warning("⚠️ يرجى ملء البيانات.")