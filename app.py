import streamlit as st
import time
import requests
from groq import Groq

# Настройка на страницата
st.set_page_config(page_title="Супер AI Температурен асистент", page_icon="🌡️", layout="wide")

# --- ИНИЦИАЛИЗИРАНЕ НА СЪСТОЯНИЕТО ---
if "temp_val" not in st.session_state:
    st.session_state.temp_val = 22.0
if "slider_input" not in st.session_state:
    st.session_state.slider_input = 22.0
if "num_input" not in st.session_state:
    st.session_state.num_input = 22.0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def sync_inputs(source_key):
    val = float(st.session_state[source_key])
    st.session_state.temp_val = val
    if source_key == "slider_input":
        st.session_state.num_input = val
    elif source_key == "num_input":
        st.session_state.slider_input = val

def set_preset_temperature(val):
    st.session_state.temp_val = float(val)
    st.session_state.slider_input = float(val)
    st.session_state.num_input = float(val)

# --- ФУНКЦИЯ ЗА ВЗЕМАНЕ НА РЕАЛНО ВРЕМЕ ---
def get_live_weather(city_name):
    try:
        api_key = st.secrets["OPENWEATHER_API_KEY"]
        url = f"http://openweathermap.org{city_name},BG&appid={api_key}&units=metric&lang=bg"
        res = requests.get(url).json()
        if res.get("cod") == 200:
            return float(res["main"]["temp"]), res["weather"][0]["description"]
        else:
            return None, "Градът не е намерен"
    except Exception:
        # Автоматичен демо режим за симулация, ако няма въведен OpenWeather ключ
        import random
        demo_temps = {"София": 12.5, "Пловдив": 15.0, "Варна": 18.2, "Бургас": 17.9, "Русе": 9.0}
        return demo_temps.get(city_name, random.uniform(5.0, 25.0)), "Разкъсана облачност (Демо режим)"

st.title("🌡️ Супер AI Температурен асистент")

# --- СТРАНИЧНА ЛЕНТА (SIDEBAR): Истинско време и Персони ---
with st.sidebar:
    st.header("⚙️ Опции и Екстри")
    
    # ИДЕЯ 1: Персона на AI
    st.subheader("👤 Избери характер на AI:")
    persona = st.selectbox(
        "Кой искаш да ти даде съвет?",
        ["Грижовната Баба 👵", "Саркастичният Комедиант 🎭", "Професионалният Метеоролог 📊"]
    )
    
    # Дефиниране на системния промпт спрямо избраната персона
    persona_prompts = {
        "Грижовната Баба 👵": "Ти си любяща, но изключително притеснена българска баба. Караш се на потребителя, ако не носи шапка, настояваш да си обуе вълнени чорапи, предлагаш му топла супа или чай и говориш мило, използвайки думи като 'чедо', 'бабиното' и 'настинка'.",
        "Саркастичният Комедиант 🎭": "Ти си изключително саркастичен и забавен стендъп комедиант. Подиграваш се на избора на температура, даваш абсурдни и смешни съвети за оцеляване и използваш черен хумор и ирония.",
        "Професионалният Метеоролог 📊": "Ти си сериозен, научен метеоролог и климатолог. Даваш точни, научно обосновани съвети за обличане, атмосферно налягане, хидратация и UV индекс с висок професионализъм."
    }
    
    st.write("---")
    
    # ИДЕЯ 2: Интеграция с реално време
    st.subheader("🌍 Вземи времето на живо:")
    city = st.text_input("Въведи град в България:", placeholder="напр. София, Варна...")
    if st.button("Вземи температурата"):
        if city:
            live_temp, desc = get_live_weather(city)
            if live_temp is not None:
                set_preset_temperature(live_temp)
                st.success(f"Успешно взето: {live_temp}°C, {desc}")
            else:
                st.error(f"Грешка: {desc}")
        else:
            st.warning("Моля, въведете име на град.")

# --- ОСНОВЕН ПАНЕЛ: Разделяне на Термометър и Контроли ---
main_col, thermo_col = st.columns([3, 1])

with main_col:
    st.subheader("Изберете температура ръчно:")
    
    # Бързи бутони
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.button("❄️ Зимна (-5°C)", use_container_width=True, on_click=set_preset_temperature, args=(-5.0,))
    with col_b2:
        st.button("🏠 Стайна (22°C)", use_container_width=True, on_click=set_preset_temperature, args=(22.0,))
    with col_b3:
        st.button("🔥 Лятна жега (35°C)", use_container_width=True, on_click=set_preset_temperature, args=(35.0,))

    # Слайдер и Нумерично поле
    c1, c2 = st.columns(2)
    with c1:
        st.slider("Плъзгач:", min_value=-30.0, max_value=50.0, key="slider_input", step=0.5, on_change=sync_inputs, args=("slider_input",))
    with c2:
        st.number_input("Точно въвеждане:", min_value=-30.0, max_value=50.0, key="num_input", step=0.1, on_change=sync_inputs, args=("num_input",))

    temperature = st.session_state.temp_val
    st.markdown(f"### Текущо избрана температура: **{temperature:.1f} °C**")

# ИДЕЯ 3: Визуален интерактивен термометър (Стилизиран с CSS и HTML)
with thermo_col:
    st.subheader("Термометър")
    clamped_temp = max(-30.0, min(50.0, temperature))
    percentage = ((clamped_temp + 30) / 80) * 100
    
    if temperature < 10: 
        mercury_color = "#00b4d8"
    elif temperature < 20: 
        mercury_color = "#2a9d8f"
    elif temperature < 30: 
        mercury_color = "#f4a261"
    else: 
        mercury_color = "#e63946"
    
    st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 220px; background: rgba(255,255,255,0.1); border-radius: 15px; padding: 10px;">
            <div style="position: relative; width: 24px; height: 140px; background: #e0e0e0; border-radius: 12px; border: 2px solid #fff; overflow: hidden; display: flex; align-items: flex-end;">
                <div style="width: 100%; height: {percentage}%; background: {mercury_color}; transition: height 0.5s ease, background-color 0.5s ease;"></div>
            </div>
            <div style="width: 36px; height: 36px; background: {mercury_color}; border-radius: 50%; margin-top: -10px; border: 2px solid #fff; transition: background-color 0.5s ease;"></div>
            <div style="margin-top: 8px; font-weight: bold; color: white;">{temperature:.1f}°C</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- ДИНАМИЧЕН ЦВЯТ НА ЦЯЛОТО ПРИЛОЖЕНИЕ ---
if temperature < 10: 
    bg_color = "#007791"
elif temperature < 20: 
    bg_color = "#2E7D32"
elif temperature < 30: 
    bg_color = "#FF8F00"
else: 
    bg_color = "#C62828"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; transition: background-color 0.5s ease; }}
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, .stSubheader {{ color: #FFFFFF !important; }}
    .stNumberInput input, .stTextInput input {{ color: #31333F !important; }}
    .stSelectbox div[data-baseweb="select"] {{ color: #31333F !important; }}
    .stButton>button {{ border: 2px solid white !important; background-color: rgba(255, 255, 255, 0.1) !important; color: white !important; }}
    .stButton>button:hover {{ background-color: rgba(255, 255, 255, 0.3) !important; color: white !important; }}
    </style>
    """,
    unsafe_allow_html=True
)

# Проверка на API Ключ за Groq
try:
    api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("❌ Грешка: Не е намерен 'GROQ_API_KEY'!")
    st.stop()

if "weather_message" not in st.session_state:
    st.session_state.weather_message = None
if "current_ai_response" not in st.session_state:
    st.session_state.current_ai_response = None

# --- БУТОН ЗА СТАРТИРАНЕ НА AI АНАЛИЗ ---
if st.button("Провери с AI", type="primary", use_container_width=True):
    st.session_state.weather_message = None
    st.session_state.current_ai_response = None
    
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

    placeholder = st.empty()
    for i in range(6):
        frame = animation_frames[i % len(animation_frames)]
        placeholder.markdown(f"<h1 style='text-align:center;'>{frame}</h1>", unsafe_allow_html=True)
        time.sleep(0.2)
    placeholder.empty()

    try:
        client = Groq(api_key=api_key)
        with st.spinner(f"🤖 {persona} обмисля съветите си..."):
            st.session_state.chat_history = [
                {"role": "system", "content": f"{persona_prompts[persona]} Важно: Винаги помни историята на разговора ни."}
            ]
            
            prompt = (
                f"Сега температурата е {temperature} градуса по Целзий. "
                f"Дай кратък, практичен и забавен съвет в 3 точки съобразно твоя характер: "
                f"1. Как да се облечем. 2. Какво да правим. 3. Важен съвет за здравето/сезона. "
                f"Ако преди това сме обсъждали друга температура, направи забавно сравнение или коментар за промяната. "
                f"Отговори на български език, използвай много емоджита."
            )
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            chat_completion = client.chat.completions.create(
                messages=st.session_state.chat_history,
                model="openai/gpt-oss-20b",
            )
            
            response_text = chat_completion.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": response_text})
            st.session_state.current_ai_response = response_text

    except Exception as e:
        st.error(f"Грешка при комуникацията с Groq: {e}")
        st.session_state.current_ai_response = None

# Извеждане на крайния резултат
if st.session_state.weather_message:
    st.info(st.session_state.weather_message)
if st.session_state.current_ai_response:
    st.subheader(f"🤖 Съвет от {persona}:")
    st.markdown(st.session_state.current_ai_response)
