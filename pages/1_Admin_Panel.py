import streamlit as st
from supabase import create_client, Client

# 1. Инициализация Supabase в самом верху
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Дашборд аналитика | SA Copilot", page_icon="🗄️", layout="wide")

# ================= ЛОГИКА АВТОРИЗАЦИИ =================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Вход для сотрудников Digital Office")
    pwd = st.text_input("Пароль", type="password")
    if st.button("Войти", type="primary"):
        if pwd == st.secrets["ADMIN_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Неверный пароль")
    st.stop() 

# ================= ДАШБОРД (Контент после авторизации) =================
st.title("🗄️ Бэклог и аналитика заявок")

# Тот самый блок, который ты прислал:
try:
    # Тянем данные из базы
    response = supabase.table("requests").select("*").order("created_at", desc=True).execute()
    tasks = response.data
    
    if not tasks:
        st.write("Пока нет новых заявок.")
    
    for task in tasks:
        # Создаем выпадающий список для каждой задачи
        with st.expander(f"🚀 {task['task_name']} (От: {task['fio']})"):
            col_biz, col_ai = st.columns(2)
            
            with col_biz:
                st.markdown("### 📋 Данные бизнеса")
                biz = task['business_data']
                st.write(f"**Департамент:** {biz.get('department', 'Не указан')}")
                st.write(f"**Проблема:** {biz.get('problem', 'Нет описания')}")
                
                # Достаем оценки
                scores = biz.get('scores', {})
                st.metric("Priority (BV/CT/RR)", f"{scores.get('BV', '?')}/{scores.get('CT', '?')}/{scores.get('RR', '?')}")

            with col_ai:
                st.markdown("### 🤖 ИИ-Анализ")
                # Здесь пока вердикт от Gemini Flash (Гейткипера)
                st.json(task['ai_analysis'])
                
                # Кнопка для запуска Копайлота
                if st.button("Запустить Копайлота (Gemini 1.5 Pro)", key=f"ai_{task['id']}"):
                    # Сохраняем ID задачи в сессию, чтобы модель знала, что анализировать
                    st.session_state.current_task_id = task['id']
                    st.info("Вызываем тяжелую артиллерию для глубокой аналитики и ТЗ...")
                    
                    # СЮДА МЫ СЕЙЧАС ДОБАВИМ ВЫЗОВ GEMINI 1.5 PRO
                    
except Exception as e:
    st.error(f"Ошибка загрузки данных из Supabase: {e}")
