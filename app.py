import streamlit as st
import google.generativeai as genai
import time

# Настройка на страницата
st.set_page_config(page_title="AI Температурен помощник", page_icon="🌡️")

st.title("🌡️ AI Температурен помощник")

# Автоматично и сигурно вземане на API ключа от secrets.toml
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("❌ Грешка: Не е намерен 'GEMINI_API_KEY' в конфигурационните файлове!")
    st.info("💡 Моля, създайте файл `.streamlit/secrets.toml` и добавете вашия ключ там.")
    st.stop()

temperature = st.number_input("Въведи температурата в °C:", min_value=-50, max_value=60, value=20)

# Инициализиране на състоянието за запазване на резултатите
if "ai_response" not in st.session_state:
    st.session_state.ai_response = None
if "weather_message" not in st.session_state:
    st.session_state.weather_message = None

if st.button("Провери", type="primary"):
    # Ограничаване на съобщението и фреймовете за анимация
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

    # Извикване на AI модела с автоматичния ключ
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        with st.spinner("🤖 AI обмисля най-добрите съвети..."):
            prompt = (
                f"Температурата е {temperature} градуса по Целзий. "
                f"Дай кратък, практичен и забавен съвет в 3 точки: "
                f"1. Как да се облечем. 2. Какво да правим навън/вкъщи. 3. Важен съвет за здравето. "
                f"Отговори на български език, използвай подходящи емоджита."
            )
            response = model.generate_content(prompt)
            st.session_state.ai_response = response.text
    except Exception as e:
        st.error(f"Грешка при комуникацията с AI: {e}")
        st.session_state.ai_response = None

# Извеждане на резултатите на екрана (за да не изчезват при рефреш)
if st.session_state.weather_message:
    st.info(st.session_state.weather_message)

if st.session_state.ai_response:
    st.subheader("🤖 AI съвет за деня:")
    st.markdown(st.session_state.ai_response)
