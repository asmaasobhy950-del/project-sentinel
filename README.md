# Project Sentinel 🤖
project_sentinel/
│
├── app.py                 # الواجهة الرسومية للمنتج (Streamlit UI)
├── agent_core.py          # عقل الـ Agent (الاتصال بـ Postgres و Gemini AI)
├── notifier.py            # قنوات التوصيل (إرسال الـ Gmail والـ WhatsApp)
├── Dockerfile             # ملف تغليف التطبيق وتحويله لـ Container
├── docker-compose.yml     # ملف تشغيل الـ Database والـ Agent معاً بـ أمر واحد
└── requirements.txt  
An intelligent, integrated task and project management system designed specifically to enhance team productivity and monitor workflow performance in real-time.

## 🚀 About the Project
**Project Sentinel** is a web application built with **Streamlit** and integrated with a **PostgreSQL** database. The system empowers managers and teams to manage tasks, monitor statuses, and generate intelligent reports using AI (Gemini).

## ✨ Key Features
* **Dashboard:** A comprehensive view of task statistics and team workload distribution.
* **Task Management:** Seamlessly add, update, and delete tasks.
* **Company Support:** Ability to categorize tasks by company and project.
* **Intelligent Reporting:** Utilizing Google Gemini AI to analyze team performance and generate administrative reports.
* **Advanced Filters:** Filter data by status, assigned employee, or company.
* **Audit Logs:** Track all changes and operations within the system.

## 🛠 Tech Stack
* **Frontend:** [Streamlit](https://streamlit.io/)
* **Database:** PostgreSQL (via `psycopg2`)
* **AI Integration:** Google Generative AI (Gemini)
* **Data Analysis:** Pandas, Plotly

## 📦 Project Structure
* `app.py`: The main application interface file.
* `agent_core.py`: Contains database connection logic and backend functions.

## ⚙️ Installation & Setup
1. Set up the required database schema.
2. Ensure the following environment variables (Secrets) are configured in Streamlit:
   - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`
   - `GEMINI_API_KEY`
3. Run the application using the command:
   ```bash
   streamlit run app.py
