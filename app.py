import streamlit as st
import google.generativeai as genai
import time

st.title("🌡️ AI Температурен помощник")

# AI настройки
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-2.0-flash")

temperature = st.number_input(
    "Въведи температурата в °C:",
    min_value=-50,
    max_value=60,
    value=20
)

if st.button("Провери"):

    if temperature < 10:
        message = "🥶 Студено е!"
        animation = "❄️ 🌨️ ❄️"

    elif temperature < 20:
        message = "🌥️ Прохладно е."
        animation = "☁️ 🌤️ ☁️"

    elif temperature < 30:
        message = "☀️ Приятно топло е!"
        animation = "🌤️ ☀️ 🌤️"

    else:
        message = "🔥 Много е горещо!"
        animation = "☀️ 🔥 ☀️"

    st.info(message)

    placeholder = st.empty()

    for i in range(10):
        placeholder.markdown(
            f"<h1 style='text-align:center'>{animation}</h1>",
            unsafe_allow_html=True
        )
        time.sleep(0.3)

    # AI генерира съвет
    with st.spinner("🤖 AI мисли..."):
        response = model.generate_content(
            f"Температурата е {temperature} градуса по Целзий. "
            "Дай кратък и полезен съвет как да се облечем "
            "и какво да правим според времето. Отговори на български."
        )

    st.subheader("🤖 AI съвет:")
    st.write(response.text)
