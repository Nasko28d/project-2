import streamlit as st
import time
from groq import Groq

# Настройка на страницата
st.set_page_config(page_title="AI Температурен помощник", page_icon="🌡️")

# Инициализиране на температурата по подразбиране в състоянието на сесията
if "temp_val" not in st.session_state:
    st.session_state.temp_val = 20.0

# Функция за обновяване на температурата при използване на контроли
def update_temp(key):
    st.session_state.temp_val = float(st.session_state[key])

st.title("🌡️ AI Температурен помощник")

# --- СЕКЦИЯ: НАЧИНИ ЗА ВЪВЕЖДАНЕ ---
st.subheader("Изберете температура по вашия любим начин:")

# Начин 1: Бързи бутони (Preset Buttons)
col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    if st.button("❄️ Зимна (-5°C)", use_container_width=True):
        st.session_state.temp_val = -5.0
with col_b2:
    if st.button("🏠 Стайна (22°C)", use_container_width=True):
        st.session_state.temp_val = 22.0
with col_b3:
    if st.button("🔥 Лятна жега (35°C)", use_container_width=True):
        st.session_state.temp_val = 35.0

# Начин 2 & 3: Плъзгач и Точно поле (разположени едно до друго)
col1, col2 = st.columns([2, 1])

with col1:
    temperature_slider = st.slider(
        "Използвай плъзгача:", 
        min_value=-50.0, 
        max_value=60.0, 
        value=float(st.session_state.temp_val),
        step=0.5,
        key="slider_input",
        on_change=update_temp,
        args=("slider_input",)
    )

with col2:
    temperature_num = st.number_input(
        "Или въведи точно:", 
        min_value=-50.0, 
        max_value=60.0, 
        value=float(st.session_state.temp_val),
        step=0.1,
        key="num_input",
        on_change=update_temp,
        args=("num_input",)
    )

# Финалната стойност, която ще се използва за изчисленията
temperature = st.session_state.temp_val

# Показваме текущо избраната температура с по-голям текст
st.markdown(f"### Текущо избрана температура: **{temperature:.1f} °C**")


# --- ДИНАМИЧЕН ЦВЯТ НА ФОНА И КОНТРАСТЕН ТЕКСТ ---
if temperature < 10:
    bg_color = "#E0F7FA"     # Свежо светлосиньо
    text_color = "#004D40"   # Тъмно патешко зелено/синьо
elif temperature < 20:
    bg_color = "#F1F8E9"     # Бледо пастелно зелено
    text_color = "#1B5E20"   # Тъмно горско зелено
elif temperature < 30:
    bg_color = "#FFFDF0"     # Мек, изключително блед крем/жълт фон (много по-светъл за четливост)
    text_color = "#3E2723"   # Тъмно кафяво (перфектен контраст върху жълтеникав фон)
else:
    bg_color = "#FFEBEE"     # Бледо червено
    text_color = "#B71C1C"   # Тъмно бордо

# Инжектиране на CSS за гарантиран контраст на всички текстови елементи в Streamlit
st.markdown(
    f"""
    <style>
    /* Фон на приложението */
    .stApp {{
        background-color: {bg_color} !important;
        transition: background-color 0.5s ease;
    }}
    
    /* Цвят на заглавията */
    h1, h2, h3, h4, h5, h6 {{
        color: {text_color} !important;
    }}
    
    /* Цвят на обикновения текст и параграфите */
    p, span, label, .stMarkdown {{
        color: {text_color} !important;
    }}
    
    /* Специфична корекция за текста вътре в AI отговора */
    .stMarkdown p {{
        color: {text_color} !important;
        font-weight: 500;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# Сигурно вземане на API ключа от настройките на Streamlit
try:
    api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("❌ Грешка: Не е намерен 'GROQ_API_KEY'!")
    st.info("💡 Ако тествате локално, създайте `.streamlit/secrets.toml`. Ако сте в Streamlit Cloud, добавете ключа в 'Advanced Settings'.")
    st.stop()

# Инициализиране на състоянието за запазване на резултатите от AI
if "ai_response" not in st.session_state:
    st.session_state.ai_response = None
if "weather_message" not in st.session_state:
    st.session_state.weather_message = None

if st.button("Провери с AI", type="primary", use_container_width=True):
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
                model="openai/gpt-oss-120b",
            )
            
            st.session_state.ai_response = chat_completion.choices.message.content
                
    except Exception as e:
        st.error(f"Грешка при комуникацията с Groq: {e}")
        st.session_state.ai_response = None

# Извеждане на резултатите на екрана
if st.session_state.weather_message:
    st.info(st.session_state.weather_message)

if st.session_state.ai_response:
    st.subheader("🤖 AI съвет за деня:")
    st.markdown(st.session_state.ai_response)
