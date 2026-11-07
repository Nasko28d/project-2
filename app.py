import streamlit as st
import time
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

st.title("🌡️ Супер AI Температурен асистент")

# --- СТРАНИЧНА ЛЕНТА (SIDEBAR): Персони ---
with st.sidebar:
    st.header("⚙️ Опции и Екстри")
    st.subheader("👤 Избери характер на AI:")
    persona = st.selectbox(
        "Кой искаш да ти даде съвет?",
        ["Грижовната Баба 👵", "Саркастичният Комедиант 🎭", "Професионалният Метеоролог 📊"]
    )
    
    persona_prompts = {
        "Грижовната Баба 👵": "Ти си любяща, но изключително притеснена българска баба. Караш се на потребителя, ако не носи шапка, настояваш да си обуе вълнени чорапи, предлагаш му топла супа или чай и говориш мило, използвайки думи като 'чедо', 'бабиното' и 'настинка'.",
        "Саркастичният Комедиант 🎭": "Ти си изключително саркастичен и забавен стендъп комедиант. Подиграваш се на избора на температура, даваш абсурдни и смешни съвети за оцеляване и използваш черен хумор и ирония.",
        "Професионалният Метеоролог 📊": "Ти си сериозен, научен метеоролог и климатолог. Даваш точни, научно обосновани съвети за обличане, атмосферно налягане, хидратация и UV индекс с висок професионализъм."
    }

# --- ДИНАМИЧЕН ЦВЯТ НА ПРИЛОЖЕНИЕТО ---
temperature = st.session_state.temp_val
if temperature < 5:
    bg_color = "#007791"
elif temperature < 23:
    bg_color = "#2E7D32"
elif temperature < 33:
    bg_color = "#FF8F00"
else:
    bg_color = "#C62828"

# --- ОСНОВЕН ПАНЕЛ: Балансирано разделение на колоните (2:1 мащаб) ---
main_col, info_col = st.columns([2, 1], gap="large")

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
        
    st.markdown(f"<h2 style='margin-top:20px;'>Текущо избрана температура: <b>{temperature:.1f} °C</b></h2>", unsafe_allow_html=True)
    
    st.write("")
    ai_btn = st.button("Провери с AI", type="primary", use_container_width=True)

with info_col:
    # Визуален термометър
    clamped_temp = max(-30.0, min(50.0, temperature))
    percentage = ((clamped_temp + 30) / 80) * 100
    
    if temperature < 5:
        mercury_color = "#00b4d8"
    elif temperature < 24:
        mercury_color = "#2a9d8f"
    elif temperature < 33:
        mercury_color = "#f4a261"
    else:
        mercury_color = "#e63946"
        
    st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 180px; background: rgba(255,255,255,0.15); border-radius: 15px; padding: 10px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.2);">
            <div style="position: relative; width: 20px; height: 110px; background: #e0e0e0; border-radius: 12px; border: 2px solid #fff; overflow: hidden; display: flex; align-items: flex-end;">
                <div style="width: 100%; height: {percentage}%; background: {mercury_color}; transition: height 0.5s ease, background-color 0.5s ease;"></div>
            </div>
            <div style="width: 30px; height: 30px; background: {mercury_color}; border-radius: 50%; margin-top: -8px; border: 2px solid #fff; transition: background-color 0.5s ease;"></div>
            <div style="margin-top: 5px; font-weight: bold; color: white;">{temperature:.1f}°C</div>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Статус за оцеляване
    if temperature <= -15:
        status_text = "🧊 Ледена епоха. Сибирски студ! Не излизай навън."
    elif temperature < 5:
        status_text = "🥶 Кочан студ. Всичко замръзва. Време е за чай."
    elif temperature < 15:
        status_text = "🧥 Хладинка. Свежо време, вземи си яке."
    elif temperature < 25:
        status_text = "🏝️ Райско кътче. Перфектно пролетно време."
    elif temperature < 33:
        status_text = "☀️ Жегичка. Става за плаж и басейн."
    else:
        status_text = "🌋 Адска жега! Асфалтът се топи около теб."
        
    st.markdown(f"""
        <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 12px; border-left: 5px solid #FFEB3B; margin-bottom: 20px; color: white;">
            <b style="font-size: 16px;">🚨 Статус за оцеляване:</b><br>{status_text}
        </div>
    """, unsafe_allow_html=True)
    
    # Визуален гардероб
    if temperature < 0:
        clothes = "🧥 Дебело зимно яке, 🧣 Шал, 🧤 Ръкавици, 🧦 Вълнени чорапи"
    elif temperature < 12:
        clothes = "🧥 Палто/Яке, 👖 Дълги панталони, 👟 Маратонки"
    elif temperature < 23:
        clothes = "👕 Суичър или жилетка, 👖 Дънки, 👟 Обувки"
    elif temperature < 30:
        clothes = "👕 Тениска, 🩳 Къси панталони, 👟 Сандали"
    else:
        clothes = "🩲 Бански костюм, 🩴 Джапанки, 🕶️ Очила, 🧢 Шапка"
        
    st.markdown(f"""
        <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 12px; border-left: 5px solid #4CAF50; color: white;">
            <b style="font-size: 16px;">🎒 Препоръчителен гардероб:</b><br>{clothes}
        </div>
    """, unsafe_allow_html=True)

# --- ГЛОБАЛЕН И КОРИГИРАН CSS СТИЛ ---
st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; transition: background-color 0.5s ease; }}
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, .stSubheader {{ color: #FFFFFF !important; }}
    div[data-testid="stWidgetLabel"] p, div[data-testid="stSliderHandle"] > div {{ color: #FFFFFF !important; }}
    .stNumberInput input, .stTextInput input, div[data-baseweb="select"] *, input {{ color: #FFFFFF !important; }}
    .stButton>button {{ border: 2px solid white !important; background-color: rgba(255, 255, 255, 0.1) !important; color: white !important; }}
    .stButton>button:hover {{ background-color: rgba(255, 255, 255, 0.3) !important; color: white !important; }}
    </style>
    """, unsafe_allow_html=True
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
if ai_btn:
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
            
            system_instruction = {"role": "system", "content": f"{persona_prompts[persona]} Важно: Винаги помни историята на разговора ни."}
            
            # Поддържаме правилната списъчна структура за избягване на list indices грешката
            if not st.session_state.chat_history:
                st.session_state.chat_history = [system_instruction]
            else:
                st.session_state.chat_history[0] = system_instruction

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
                model="qwen/qwen3.8-27b",
            )
            
            # Извличане на текста от модела (подсигурено за всякакви формати на обекта)
            try:
                response_text = chat_completion.choices[0].message.content
            except (AttributeError, TypeError, KeyError):
                try:
                    response_text = chat_completion.choices.message.content
                except (AttributeError, TypeError, KeyError):
                    response_text = chat_completion["choices"][0]["message"]["content"]

            st.session_state.chat_history.append({"role": "assistant", "content": response_text})
            st.session_state.current_ai_response = response_text

    except Exception as e:
        st.error(f"Грешка при комуникацията с модела: {e}")
        st.session_state.current_ai_response = None

# Извеждане на крайния резултат най-отдолу под основния панел
if st.session_state.weather_message:
    st.info(st.session_state.weather_message)
if st.session_state.current_ai_response:
    st.subheader(f"🤖 Съвет от {persona}:")
    st.markdown(st.session_state.current_ai_response)

