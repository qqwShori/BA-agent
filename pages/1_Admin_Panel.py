import streamlit as st
import json
import google.generativeai as genai
from supabase import create_client, Client

# Инициализация баз и API
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.warning("Ключ Gemini не найден, аналитика не сработает.")

st.set_page_config(page_title="Дашборд аналитика | SA Copilot", page_icon="🗄️", layout="wide")

# ================= КОНТЕКСТ СОТРУДНИКОВ =================
BA_TEAM_CONTEXT = """
Список доступных бизнес-аналитиков в департаменте:
1. Айдос: Backend, биллинг, интеграции, API, базы данных, легаси системы.
2. Динара: CX/UX, мобильное приложение TelecomKz, B2C абоненты, клиентский путь.
3. Рустам: B2B сегмент, CRM, сложные корпоративные процессы и документооборот.
4. Алина: Аналитика данных, отчетность, выгрузки, DWH, дашборды.
5. Ермек: Внутренние операции, приложение для инсталляторов, оборудование, саппорт.
"""

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

# ================= ДАШБОРД =================
st.title("🗄️ Бэклог и аналитика заявок")

try:
    response = supabase.table("requests").select("*").order("created_at", desc=True).execute()
    tasks = response.data
    
    if not tasks:
        st.write("Пока нет новых заявок.")
    
    for task in tasks:
        with st.expander(f"🚀 {task['task_name']} (От: {task['fio']})"):
            col_biz, col_ai = st.columns(2)
            biz = task['business_data']
            
            with col_biz:
                with col_biz:
                st.markdown("### 📋 Полная анкета заказчика")
                biz = task['business_data']
                
                # --- БЛОК 1: МЕТАДАННЫЕ ---
                c1, c2 = st.columns(2)
                with c1:
                    st.caption("👤 ФИО и Подразделение")
                    st.write(f"**{task['fio']}** ({biz.get('department', '—')})")
                with c2:
                    st.caption("📞 Контакт")
                    st.write(biz.get('contact', '—'))
                
                st.divider()

                # --- БЛОК 2: ПРОБЛЕМА И ЦЕЛЬ ---
                st.markdown("#### 🔍 Суть и контекст")
                
                st.markdown(f"**Что случилось?**\n\n_{biz.get('problem', '—')}_")
                st.markdown(f"**Кого касается:** {biz.get('target_audience', '—')}")
                
                with st.expander("Посмотреть идеальное решение и правила"):
                    st.markdown(f"**Как должно работать:**\n\n{biz.get('solution', '—')}")
                    st.markdown(f"**Жесткие правила:**\n\n{biz.get('rules', '—')}")
                
                st.info(f"**User Story:**\n\n{biz.get('user_story', '—')}")

                st.divider()

                # --- БЛОК 3: БИЗНЕС-ЦЕННОСТЬ И ПРИОРИТЕТЫ ---
                st.markdown("#### 💰 Ценность для компании")
                
                # Выводим показатели в ряд
                scores = biz.get('scores', {})
                m1, m2, m3 = st.columns(3)
                m1.metric("Value (BV)", f"{scores.get('BV', '?')}/7")
                m2.metric("Critical (CT)", f"{scores.get('CT', '?')}/7")
                m3.metric("Risks (RR)", f"{scores.get('RR', '?')}/7")

                with st.expander("Детальное обоснование оценок"):
                    st.markdown(f"**Польза:** {biz.get('bv_desc', '—')}")
                    st.markdown(f"**Срочность:** {biz.get('ct_desc', '—')}")
                    st.markdown(f"**Риски/Возможности:** {biz.get('rr_desc', '—')}")
                    st.success(f"**Расчеты и цифры:**\n\n{biz.get('metrics', '—')}")

            with col_ai:
                st.markdown("### 🤖 Копайлот Системного Анализа")
                
                # Кнопка для запуска (используем session_state, чтобы результат не исчезал при кликах)
                run_key = f"run_{task['id']}"
                result_key = f"res_{task['id']}"
                
                if result_key not in st.session_state:
                    if st.button("Сгенерировать ТЗ и процесс (Gemini Flash)", key=run_key, type="primary"):
                        with st.spinner("Анализирую задачу, подбираю аналитика, рисую BPMN..."):
                            
                            # Собираем данные для промпта
                            task_context = f"""
                            Задача: {task['task_name']}
                            Аудитория/Департамент: {biz.get('department', '')}
                            Проблема: {biz.get('problem', '')}
                            Ожидание: {biz.get('solution', '')}
                            Бизнес-правила: {biz.get('rules', 'Не указаны')}
                            User Story: {biz.get('user_story', '')}
                            """
                            
                            system_instruction = f"""
                            Ты Senior Business/System Analyst. 
                            1. Изучи задачу.
                            2. Выбери идеального исполнителя из списка:
                            {BA_TEAM_CONTEXT}
                            3. Сформируй драфт ТЗ.
                            4. Напиши код для диаграммы процесса в формате Mermaid.js (используй синтаксис flowchart TD или sequenceDiagram).
                            
                            Верни строго JSON:
                            {{
                                "assigned_ba": "Имя",
                                "reasoning": "Почему выбран этот аналитик",
                                "questions_for_kickoff": ["Вопрос 1", "Вопрос 2"],
                                "tz_draft": "Текст ТЗ в формате Markdown",
                                "mermaid_code": "Только сам код mermaid, без маркдаун кавычек ```"
                            }}
                            """
                            
                            model = genai.GenerativeModel(
                                "gemini-2.5-flash",
                                system_instruction=system_instruction,
                                generation_config={"response_mime_type": "application/json"}
                            )
                            
                            ai_response = model.generate_content(task_context)
                            st.session_state[result_key] = json.loads(ai_response.text)
                            st.rerun() # Перезагружаем интерфейс для отрисовки результата
                
                # Если ИИ уже отработал - показываем результат красиво
                if result_key in st.session_state:
                    ai_data = st.session_state[result_key]
                    
                    st.success(f"**Назначено:** {ai_data['assigned_ba']}")
                    st.caption(f"**Обоснование:** {ai_data['reasoning']}")
                    
                    tab1, tab2, tab3 = st.tabs(["📝 Драфт ТЗ", "📊 Диаграмма (Mermaid)", "❓ Вопросы к бизнесу"])
                    
                    with tab1:
                        st.markdown(ai_data['tz_draft'])
                    with tab2:
                        # Streamlit нативно рендерит Mermaid, если передать его в блок кода markdown!
                        st.markdown(f"```mermaid\n{ai_data['mermaid_code']}\n```")
                        with st.expander("Посмотреть исходный код диаграммы"):
                            st.code(ai_data['mermaid_code'], language="mermaid")
                    with tab3:
                        for q in ai_data['questions_for_kickoff']:
                            st.markdown(f"- {q}")
                    
except Exception as e:
    st.error(f"Ошибка загрузки данных из Supabase: {e}")
