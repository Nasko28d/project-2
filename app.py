import streamlit as st
import time
from groq import Groq

# Настройка на страницата
st.set_page_config(page_title="Супер AI Температурен асистент", page_icon="🌡️", layout="wide")

# --- ИНИЦИАЛИЗИРАНЕ НА СЪСТОЯНИЕТО ---
if "unit" not in st.session_state:
    st.session_state.unit = "°C"
if "temp_val" not in st.session_state:
    st.session_state.temp_val = 22.0
if "slider_input" not in st.session_state:
    st.session_state.slider_input = 22.0
if "num_input" not in st.session_state:
    st.session_state.num_input = 22.0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "weather_message" not in st.session_state:
    st.session_state.weather_message = None
if "current_ai_response" not in st.session_state:
    st.session_state.current_ai_response = None

# Функции за преобразуване
def c_to_f(c):
    return (c * 1.8) + 32

def f_to_c(f):
    return (f - 32) / 1.8

# Синхронизация при промяна на мерната единица от менюто
def handle_unit_change():
    current_val = st.session_state.temp_val
    if st.session_state.unit_selector == "°C" and st.session_state.unit == "°F":
        # Преминаваме от F към C
        converted = round(f_to_c(current_val), 1)
        st.session_state.unit = "°C"
    elif st.session_state.unit_selector == "°F" and st.session_state.unit == "°C":
        # Преминаваме от C към F
        converted = round(c_to_f(current_val), 1)
        st.session_state.unit = "°F"
    else:
        return
        
    st.session_state.temp_val = converted
    st.session_state.slider_input = converted
    st.session_state.num_input = converted

def sync_inputs(source_key):
    val = float(st.session_state[source_key])
    st.session_state.temp_val = val
    if source_key == "slider_input":
        st.session_state.num_input = val
    elif source_key == "num_input":
        st.session_state.slider_input = val

def set_preset_temperature(val_c):
    # Пресетите се подават в Целзий, преизчисляват се спрямо избраната единица
    if st.session_state.unit == "°F":
        val = round(c_to_f(val_c), 1)
    else:
        val = float(val_c)
    st.session_state.temp_val = val
    st.session_state.slider_input = val
    st.session_state.num_input = val

st.title("🌡️ Супер AI Температурен асистент")

# --- СТРАНИЧНА ЛЕНТА (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Опции и Екстри")
    
    # Бутон за превключване на мерната единица
    st.subheader("📏 Мерна единица:")
    st.radio(
        "Избери скала за показване:",
        ["°C", "°F"],
        key="unit_selector",
        index=0 if st.session_state.unit == "°C" else 1,
        on_change=handle_unit_change
    )
    
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

# Пресмятане на базовите стойности в Целзий за логиката на интерфейса
display_temp = st.session_state.temp_val
if st.session_state.unit == "°F":
    temp_c = f_to_c(display_temp)
    temp_f = display_temp
    min_slide, max_slide = -22.0, 122.0
else:
    temp_c = display_temp
    temp_f = c_to_f(display_temp)
    min_slide, max_slide = -30.0, 50.0

# --- ДИНАМИЧЕН ЦВЯТ НА ПРИЛОЖЕНИЕТО (РЕАЛИСТИЧЕН СПЕКТЪР НА БАЗА ЦЕЛЗИЙ) ---
if temp_c <= 0:
    clamped_cold = max(-30.0, temp_c)
    blue_ratio = (clamped_cold - (-30.0)) / 30.0
    r = int(0)
    g = int(50 + (120 * blue_ratio))
    b = int(100 + (155 * blue_ratio))
elif temp_c <= 18:
    ratio = (temp_c - 0) / 18.0
    r = int(0 + (46 * ratio))
    g = int(170 - (45 * ratio))
    b = int(255 - (205 * ratio))
elif temp_c <= 28:
    ratio = (temp_c - 18) / 10.0
    r = int(46 + (209 * ratio))
    g = int(125 + (18 * ratio))
    b = int(50 - (50 * ratio))
else:
    clamped_hot = min(45.0, temp_c)
    ratio = (clamped_hot - 28) / 17.0
    r = int(255 - (57 * ratio))
    g = int(143 - (110 * ratio))
    b = int(0 + (30 * ratio))

bg_color = f"rgb({r}, {g}, {b})"

# --- ОСНОВЕН ПАНЕЛ ---
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
        
    # Динамичен Слайдер и Нумерично поле спрямо единицата
    c1, c2 = st.columns(2)
    with c1:
        st.slider(f"Плъзгач ({st.session_state.unit}):", min_value=min_slide, max_value=max_slide, key="slider_input", step=0.5, on_change=sync_inputs, args=("slider_input",))
    with c2:
        st.number_input(f"Точно въвеждане ({st.session_state.unit}):", min_value=min_slide, max_value=max_slide, key="num_input", step=0.1, on_change=sync_inputs, args=("num_input",))
        
    st.markdown(f"<h2 style='margin-top:20px;'>Текущо избрана температура: <b>{display_temp:.1f} {st.session_state.unit}</b></h2>", unsafe_allow_html=True)
    st.write("")
    ai_btn = st.button("Провери с AI", type="primary", use_container_width=True)

with info_col:
    # Визуален термометър (Скала базирана на Целзий)
    clamped_temp = max(-30.0, min(50.0, temp_c))
    percentage = ((clamped_temp + 30) / 80) * 100
    
    if temp_c < 5:
        mercury_color = "#00b4d8"
    elif temp_c < 24:
        mercury_color = "#2a9d8f"
    elif temp_c < 33:
        mercury_color = "#f4a261"
    elif temp_c < 40:
        mercury_color = "#E34234"
    else:
        mercury_color = "#e63946"
        
    st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 180px; background: rgba(255,255,255,0.15); border-radius: 15px; padding: 10px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.2);">
            <div style="position: relative; width: 20px; height: 110px; background: #e0e0e0; border-radius: 12px; border: 2px solid #fff; overflow: hidden; display: flex; align-items: flex-end;">
                <div style="width: 100%; height: {percentage}%; background: {mercury_color}; transition: height 0.5s ease, background-color 0.5s ease;"></div>
            </div>
            <div style="width: 30px; height: 30px; background: {mercury_color}; border-radius: 50%; margin-top: -8px; border: 2px solid #fff; transition: background-color 0.5s ease;"></div>
            <div style="margin-top: 5px; font-weight: bold; color: white;">{temp_c:.1f}°C / {temp_f:.1f}°F</div>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Статус за оцеляване
    if temp_c <= -15:
        status_text = "🧊 Ледена епоха. Сибирски студ! Не излизай навън."
    elif temp_c < 0:
        status_text = "🥶 Кочан студ. Всичко замръзва. Време е за чай."
    elif temp_c < 15:
        status_text = "🧥 Хладинка. Свежо време, вземи си яке."
    elif temp_c < 25:
        status_text = "🏝️ Райско кътче. Перфектно пролетно време."
    elif temp_c < 33:
        status_text = "☀️ Жегичка. Става за плаж и басейн."
    elif temp_c < 40:
        status_text = "🌋 Адска жег! Асфалтът се топи около теб."
    else:
        status_text = "🔥 Направо пещ! Не може да се живее."
        
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 12px; border-left: 5px solid #FFEB3B; margin-bottom: 20px; color: white;">
        <b style="font-size: 16px;">🚨 Статус за оцеляване:</b><br>{status_text}
    </div>
    """, unsafe_allow_html=True)
    
    # Визуален гардероб
    if temp_c < 0:
        clothes = "🧥 Дебело зимно яке, 🧣 Шал, 🧤 Ръкавици, 🧦 Вълнени чорапи"
    elif temp_c < 12:
        clothes = "🧥 Палто/Яке, 👖 Дълги панталони, 👟 Маратонки"
    elif temp_c < 23:
        clothes = "👕 Суичър или жилетка, 👖 Дънки, 👟 Обувки"
    elif temp_c < 30:
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
    .stApp {{
        background-color: {bg_color} !important;
        transition: background-color 0.5s ease;
    }}
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, .stSubheader {{
        color: #FFFFFF !important;
    }}
    div[data-testid="stWidgetLabel"] p {{
        color: #FFFFFF !important;
    }}
    .stNumberInput input, .stTextInput input, div[data-baseweb="select"] *, input {{
        color: #FFFFFF !important;
    }}
    .stButton>button {{
        border: 2px solid white !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }}
    .stButton>button:hover {{
        background-color: rgba(255, 255, 255, 0.3) !important;
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True
)

# Проверка на API Ключ за Groq
try:
    api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("❌ Грешка: Не е намерен 'GROQ_API_KEY' в st.secrets!")
    st.stop()

# --- БУТОН ЗА СТАРТИРАНЕ НА AI АНАЛИЗ ---
if ai_btn:
    st.session_state.weather_message = None
    st.session_state.current_ai_response = None
    
    if temp_c < 10:
        st.session_state.weather_message = f"🥶 Студено е! ({temp_c:.1f}°C / {temp_f:.1f}°F)"
        animation_frames = ["❄️ 🌨️ ❄️", "🌨️ ❄️ 🌨️"]
    elif temp_c < 20:
        st.session_state.weather_message = f"🌥️ Прохладно е. ({temp_c:.1f}°C / {temp_f:.1f}°F)"
        animation_frames = ["☁️ 🌤️ ☁️", "🌤️ ☁️ 🌤️"]
    elif temp_c < 30:
        st.session_state.weather_message = f"☀️ Приятно топло е! ({temp_c:.1f}°C / {temp_f:.1f}°F)"
        animation_frames = ["🌤️ ☀️ 🌤️", "☀️ 🌤️ ☀️"]
    else:
        st.session_state.weather_message = f"🔥 Много е горещо! ({temp_c:.1f}°C / {temp_f:.1f}°F)"
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
            system_instruction = {"role": "system", "content": persona_prompts[persona]}
            prompt = (
                f"Сега температурата е {temp_c:.1f} градуса по Целзий ({temp_f:.1f} градуса по Фаренхайт). "
                f"Дай кратък, практичен и забавен съвет в 3 точки съобразно твоя характер: "
                f"1. Как да се облечем. 2. Какво да правим. 3. Важен съвет за здравето/сезона. "
                f"Ако преди това сме обсъждали друга температура, направи забавно сравнение или коментар за промяната. "
                f"Отговори на български език, използвай много емоджита."
            )
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            if len(st.session_state.chat_history) > 6:
                st.session_state.chat_history = st.session_state.chat_history[-6:]
                
            messages_to_send = [system_instruction] + st.session_state.chat_history
            
            chat_completion = client.chat.completions.create(
                messages=messages_to_send,
                model="openai/gpt-oss-20b"
            )
            
            response_text = chat_completion.choices[0].message.content
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
