import streamlit as st
import time
from groq import Groq

# Настройка на страницата
st.set_page_config(page_title="AI Температурен помощник", page_icon="🌡️")

# --- ДИНАМИЧЕН ЦВЯТ НА ФОНА ---
temperature = st.number_input("Въведи температурата в °C:", min_value=-50, max_value=60, value=20)

# Определяне на цвят на фона според температурата (меки, пастелни тонове за по-добър UX)
if temperature < 10:
    bg_color = "#E0F7FA"  # Свежо светлосиньо (студено)
    text_color = "#006064"
elif temperature < 20:
    bg_color = "#F1F8E9"  # Бледозелено/прохладно
    text_color = "#33691E"
elif temperature < 30:
    bg_color = "#FFFDE7"  # Мек топъл жълт цвят
    text_color = "#F57F17"
else:
    bg_color = "#FFEBEE"  # Бледочервено (горещо)
    text_color = "#B71C1C"

# Инжектиране на CSS за промяна на background-а и добавяне на плавен преход (transition)
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color} !important;
        transition: background-color 0.5s ease;
    }}
    /* Опционално: промяна на цвета на заглавието за по-добър контраст */
    h1, h2, h3 {{
        color: {text_color} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌡️ AI Температурен помощник")

# Сигурно вземане на API ключа от настройките на Streamlit
try:
    api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("❌ Грешка: Не е намерен 'GROQ_API_KEY'!")
    st.info("💡 Ако тествате локално, създайте `.streamlit/secrets.toml`. Ако сте в Streamlit Cloud, добавете ключа в 'Advanced Settings'.")
    st.stop()

# Инициализиране на състоянието за запазване на резултатите
if "ai_response" not in st.session_state:
    st.session_state.ai_response = None
if "weather_message" not in st.session_state:
    st.session_state.weather_message = None

if st.button("Провери", type="primary"):
    # Изчистване на старите резултати при ново натискане
    st.session_state.ai_response = None
    st.session_state.weather_message = None

    # Определяне на съобщението и анимацията
    if temperature < 10:
        st.session_state.weather_message = "🥶 Студено е!"
        animation_frames = ["❄️ 🌨️ ❄️", "🌨️ ❄️ 🌨️"]
    elif temperature < 20:
        st.session_state.weather_message = "🌥️ Прохладно е."
        animation_frames = ["☁️ 🌤️ ☁️", "🌤️ ☁️ 🌤️"]
    elif temperature < 30:
        st.session_state.weather_message = "☀️ Приятно топло е!"
        animation_frames = ["🌤️ ☀️ 🌤️", "☀️ 🌤️ ☀️"]
    else:
        st.session_state.weather_message = "🔥 Много е горещо!"
        animation_frames = ["☀️ 🔥 ☀️", "🔥 ☀️ 🔥"]

    # Кратка премигваща анимация
    placeholder = st.empty()
    for i in range(6):
        frame = animation_frames[i % len(animation_frames)]
        placeholder.markdown(f"<h1 style='text-align:center;'>{frame}</h1>", unsafe_allow_html=True)
        time.sleep(0.3)
    placeholder.empty()

    # Извикване на AI модела през Groq
    try:
        client = Groq(api_key=api_key)
        
        with st.spinner("🤖 AI обмисля най-добрите съвети през Groq..."):
            prompt = (
                f"Температурата е {temperature} градуса по Целзий. "
                f"Дай кратък, практичен и забавен съвет в 3 точки: "
                f"1. Как да се облечем. 2. Какво да правим навън/вкъщи. 3. Важен съвет за здравето. "
                f"Отговори на български език, използвай подходящи емоджита."
            )
            
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
            
            st.session_state.ai_response = chat_completion.choices[0].message.content
                
    except Exception as e:
        st.error(f"Грешка при комуникацията с Groq: {e}")
        st.session_state.ai_response = None

# Извеждане на резултатите на екрана
if st.session_state.weather_message:
    st.info(st.session_state.weather_message)

if st.session_state.ai_response:
    st.subheader("🤖 AI съвет за деня:")
    st.markdown(st.session_state.ai_response)
