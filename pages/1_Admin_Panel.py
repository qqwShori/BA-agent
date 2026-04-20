import streamlit as st
import pandas as pd # Понадобится для красивой отрисовки таблиц

st.set_page_config(page_title="Дашборд аналитика | SA Copilot", page_icon="🗄️", layout="wide")

# ================= ЛОГИКА АВТОРИЗАЦИИ =================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Вход для сотрудников Digital Office")
    st.info("Пожалуйста, введите пароль для доступа к дашборду заявок.")
    
    pwd = st.text_input("Пароль", type="password")
    if st.button("Войти", type="primary"):
        if pwd == st.secrets["ADMIN_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun() # Перезагружаем страницу, чтобы скрыть форму входа
        else:
            st.error("❌ Неверный пароль")
    
    st.stop() # Этот метод не дает коду выполняться дальше, пока не введен пароль

# ================= ДАШБОРД (Виден только после входа) =================
st.title("🗄️ Бэклог и аналитика заявок")

# Позже здесь будет вызов (например, из Supabase) для получения списка задач
# А пока сделаем Mock-данные (заглушку), чтобы ты оценил визуал:

st.subheader("Ожидают взятия в работу")

# Пример того, как мы будем выводить сгенерированные данные
mock_task = st.expander("🚀 Временное отключение в приложении TelecomKz (Приоритет: Высокий)")
with mock_task:
    # Делим экран: слева вводные бизнеса, справа - работа Копайлота
    col_biz, col_ai = st.columns(2)
    
    with col_biz:
        st.markdown("### 📋 Исходные данные от бизнеса")
        st.write("**Заказчик:** Иванов И.И. (B2C)")
        st.write("**Проблема:** Клиенты жалуются, что не могут временно заморозить интернет...")
        st.write("**User Story:** Я, как абонент, хочу нажать одну кнопку, чтобы заморозить списание средств.")
        st.metric(label="Business Value", value="6/7")
        st.metric(label="Time Criticality", value="4/7")

    with col_ai:
        st.markdown("### 🤖 Аналитика и драфт ТЗ (ИИ)")
        st.info("**Рекомендация агента:** Задача хорошо описана. Риск: не указано, что делать с абонентами с задолженностью.")
        
        # Вкладки для удобной работы аналитика
        tab1, tab2 = st.tabs(["Черновик ТЗ", "BPMN / UML код"])
        with tab1:
            st.text_area("Драфт ТЗ", "1. Цель...\n2. Предусловия...\n3. Основной сценарий (Happy path)...", height=200)
        with tab2:
            st.code("""
@startuml
actor Абонент
participant "Мобильное приложение" as App
participant "Биллинг" as Billing

Абонент -> App: Нажимает "Временное отключение"
App -> Billing: Проверка баланса
alt Баланс > 0
    Billing --> App: Ок, заморозка возможна
else Баланс < 0
    Billing --> App: Ошибка, есть долг
end
@enduml
            """, language="plantuml")

    # Кнопка для перевода статуса
    if st.button("Принять в системный анализ", key="take_task_1"):
        st.success("Задача переведена в Jira/взята в работу!")
