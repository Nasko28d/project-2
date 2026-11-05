import streamlit as st
import google.generativeai as genai
import time

# Заглавие на приложението
st.title("🌡️ AI Температурен помощник")

# Сигурно въвеждане на API ключ през страничното меню
api_key = st.sidebar.text_input("Въведете вашия Gemini API Ключ:", type="password")

temperature = st.number_input("Въведи температурата в °C:", min_value=-50, max_value=60, value=20)

if st.button("Провери"):
    if temperature < 10:
        message = "🥶 Студено е!"
        animation_frames = ["❄️ 🌨️ ❄️", "🌨️ ❄️ 🌨️"]
    elif temperature < 20:
        message = "🌥️ Прохладно е."
        animation_frames = ["☁️ 🌤️ ☁️", "🌤️ ☁️ 🌤️"]
    elif temperature < 30:
        message = "☀️ Приятно топло е!"
        animation_frames = ["🌤️ ☀️ 🌤️", "☀️ 🌤️ ☀️"]
    else:
        message = "🔥 Много е горещо!"
        animation_frames = ["☀️ 🔥 ☀️", "🔥 ☀️ 🔥"]

    st.info(message)
    
    # Истинска премигваща анимация
    placeholder = st.empty()
    for i in range(10):
        frame = animation_frames[i % len(animation_frames)]
        placeholder.markdown(f"<h1 style='text-align:center;'>{frame}</h1>", unsafe_allow_html=True)
        time.sleep(0.3)
    placeholder.empty()

    # Извикване на AI модела само ако има предоставен ключ
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            
            with st.spinner("🤖 AI мисли..."):
                prompt = f"Температурата е {temperature} градуса по Целзий. Дай кратък и полезен съвет как да се облечем и какво да правим според времето. Отговори на български."
                response = model.generate_content(prompt)
                
            st.subheader("🤖 AI съвет:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Грешка при комуникацията с AI: {e}")
    else:
        st.warning("⚠️ Моля, въведете вашия Gemini API ключ в страничното меню, за да получите AI съвет.")
