import streamlit as st
import time
from groq import Groq  # Импортираме правилната библиотека

# Настройка на страницата
st.set_page_config(page_title="AI Температурен помощник", page_icon="🌡️")
st.title("🌡️ AI Температурен помощник")

# Сигурно вземане на API ключа от настройките на Streamlit
try:
    api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("❌ Грешка: Не е намерен 'GROQ_API_KEY'!")
    st.info("💡 Ако тествате локално, създайте `.streamlit/secrets.toml`. Ако сте в Streamlit Cloud, добавете ключа в 'Advanced Settings'.")
    st.stop()

temperature = st.number_input("Въведи температурата в °C:", min_value=-50, max_value=60, value=20)

# Инициализиране на състоянието за запазване на резултатите
if "ai_response" not in st.session_state:
    st.session_state.ai_response = None
if "weather_message" not in st.session_state:
    st.session_state.weather_message = None

if st.button("Провери", type="primary"):
    # Изчистване на старите резултати при ново натискане (за по-добър UX)
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
            
            # Използваме новия актуален и поддържан модел qwen/qwen3.8-27b
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="qwen/qwen3.8-27b",
            )
            
            # Безопасно извличане на текста, съвместимо с новите модели
            first_choice = chat_completion.choices[0]
            if hasattr(first_choice, 'message'):
                st.session_state.ai_response = first_choice.message.content
            else:
                st.session_state.ai_response = first_choice['message']['content']
                
    except Exception as e:
        st.error(f"Грешка при комуникацията с Groq: {e}")
        st.session_state.ai_response = None

# Извеждане на резултатите на екрана
if st.session_state.weather_message:
    st.info(st.session_state.weather_message)

if st.session_state.ai_response:
    st.subheader("🤖 AI съвет за деня:")
    st.markdown(st.session_state.ai_response)
