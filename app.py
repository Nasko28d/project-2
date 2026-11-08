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
if "weather_message" not in st.session_state:
    st.session_state.weather_message = None
if "current_ai_response" not in st.session_state:
    st.session_state.current_ai_response = None

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
        "Грижовната Баба 👵": "Ти си любяща, но изключително притеснена българска баба. Караш се на потребителя, ако не носи шапка, настояваш да си обуе вълнени чорапи, предлагаш му топла супа или чай и говориш мило, използвайки думи като 'чедо', 'бабиното' и 'настинка'. Коментирай температурата както в Целзий, така и в нейния Фаренхайт еквивалент, за да звучиш още по-забавно разтревожена.",
        "Саркастичният Комедиант 🎭": "Ти си изключително саркастичен и забавен стендъп комедиант. Подиграваш се на избора на температура, даваш абсурдни и смешни съвети за оцеляване и използваш черен хумор и ирония. Сравни стойностите в Целзий и Фаренхайт по ироничен и абсурден начин.",
        "Професионалният Метеоролог 📊": "Ти си сериозен, научен метеоролог и климатолог. Даваш точни, научно обосновани съвети за обличане, атмосферно налягане, хидратация и UV индекс с висок професионализъм. Спомени прецизно и двете скали (°C и °F) в твоя научен доклад."
    }

# --- ДИНАМИЧЕН ЦВЯТ НА ПРИЛОЖЕНИЕТО (РЕАЛИСТИЧЕН СПЕКТЪР) ---
temperature = st.session_state.temp_val
temperature_f = (temperature * 1.8) + 32

if temperature <= 0:
    clamped_cold = max(-30.0, temperature)
    blue_ratio = (clamped_cold - (-30.0)) / 30.0
    r = int(0)
    g = int(50 + (120 * blue_ratio))
    b = int(100 + (155 * blue_ratio))
elif temperature <= 18:
    ratio = (temperature - 0) / 18.0
    r = int(0 + (46 * ratio))
    g = int(170 - (45 * ratio))
    b = int(255 - (205 * ratio))
elif temperature <= 28:
    ratio = (temperature - 18) / 10.0
    r = int(46 + (209 * ratio))
    g = int(125 + (18 * ratio))
    b = int(50 - (50 * ratio))
else:
    clamped_hot = min(45.0, temperature)
    ratio = (clamped_hot - 28) / 17.0
    r = int(255 - (57 * ratio))
    g = int(143 - (110 * ratio))
    b = int(0 + (30 * ratio))

bg_color = f"rgb({r}, {g}, {b})"

# --- ОСНОВЕН ПАНЕЛ ---
main_col, info_col = st.columns([2, 1], gap="large")

with main_col:
    st.subheader("Изберете температура ръчно:")
    
    # Бързи бутони с двете мерни единици
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.button("❄️ Зимна (-5°C / 23°F)", use_container_width=True, on_click=set_preset_temperature, args=(-5.0,))
    with col_b2:
        st.button("🏠 Стайна (22°C / 71.6°F)", use_container_width=True, on_click=set_preset_temperature, args=(22.0,))
    with col_b3:
        st.button("🔥 Лятна жега (35°C / 95°F)", use_container_width=True, on_click=set_preset_temperature, args=(35.0,))
        
    # Слайдер и Нумерично поле
    c1, c2 = st.columns(2)
    with c1:
        st.slider("Плъзгач (°C):", min_value=-30.0, max_value=50.0, key="slider_input", step=0.5, on_change=sync_inputs, args=("slider_input",))
    with c2:
        st.number_input("Точно въвеждане (°C):", min_value=-30.0, max_value=50.0, key="num_input", step=0.1, on_change=sync_inputs, args=("num_input",))
        
    st.markdown(f"<h2 style='margin-top:20px;'>Текущо избрана температура: <b>{temperature:.1f} °C</b> / <b>{temperature_f:.1f} °F</b></h2>", unsafe_allow_html=True)
    st.write("")
    ai_btn = st.button("Провери с AI", type="primary", use_container_width=True)

with info_col:
    # --- ВИЗУАЛЕН ТЕРМОМЕТЪР С НАПЪЛНО СИМЕТРИЧНА ДВОЙНА СКАЛА (°C и °F) ---
    clamped_temp = max(-30.0, min(50.0, temperature))
    percentage = ((clamped_temp + 30) / 80) * 100
    
    if temperature < 5:
        mercury_color = "#00b4d8"
    elif temperature < 24:
        mercury_color = "#2a9d8f"
    elif temperature < 33:
        mercury_color = "#f4a261"
    elif temperature < 40:
        mercury_color = "#E34234"
    else:
        mercury_color = "#e63946"
        
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: center; height: 240px; background: rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.15);">
            <!-- Скала Целзий (Отляво) -->
            <div style="display: flex; flex-direction: column; justify-content: space-between; height: 140px; text-align: right; margin-right: 12px; font-family: monospace; font-size: 11px; color: rgba(255,255,255,0.8); line-height: 1;">
                <div>50°C —</div>
                <div>30°C —</div>
                <div>10°C —</div>
                <div>-10°C —</div>
                <div>-30°C —</div>
            </div>
            
            <!-- Тяло на термометъра (Перфектно подравнено по центъра) -->
            <div style="display: flex; flex-direction: column; align-items: center; position: relative;">
                <!-- Стъклена тръбичка -->
                <div style="position: relative; width: 16px; height: 140px; background: rgba(255,255,255,0.2); border-radius: 8px; border: 2px solid #fff; overflow: hidden; display: flex; align-items: flex-end; z-index: 2;">
                    <!-- Живачен стълб -->
                    <div style="width: 100%; height: {percentage}%; background: {mercury_color}; transition: height 0.5s ease, background-color 0.5s ease;"></div>
                </div>
                <!-- Резервоар -->
                <div style="width: 26px; height: 26px; background: {mercury_color}; border-radius: 50%; margin-top: -6px; border: 2px solid #fff; transition: background-color 0.5s ease; z-index: 1;"></div>
            </div>
            
            <!-- Скала Фаренхайт (Отдясно) -->
            <div style="display: flex; flex-direction: column; justify-content: space-between; height: 140px; text-align: left; margin-left: 12px; font-family: monospace; font-size: 11px; color: rgba(255,255,255,0.8); line-height: 1;">
                <div>— 122°F</div>
                <div>— 86°F</div>
                <div>— 50°F</div>
                <div>— 14°F</div>
                <div>— -22°F</div>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Дигитален дисплей под термометъра
    st.markdown(
        f"""
        <div style="text-align: center; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05);">
            <span style="font-size: 22px; font-weight: bold; color: white; display: block;">{temperature:.1f} °C</span>
            <span style="font-size: 16px; color: rgba(255,255,255,0.7); font-weight: 500;">{temperature_f:.1f} °F</span>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Статус за оцеляване (С добавени °C и °F)
    if temperature <= -15:
        status_text = f"🧊 Ледена епоха. Сибирски студ ({temperature:.0f}°C / {temperature_f:.0f}°F)! Не излизай навън."
    elif temperature < 0:
        status_text = f"🥶 Кочан студ ({temperature:.0f}°C / {temperature_f:.0f}°F). Всичко замръзва. Време е за чай."
    elif temperature < 15:
        status_text = f"🧥 Хладинка ({temperature:.0f}°C / {temperature_f:.0f}°F). Свежо време, вземи си яке."
    elif temperature < 25:
        status_text = f"🏝️ Райско кътче ({temperature:.0f}°C / {temperature_f:.0f}°F). Перфектно пролетно време."
    elif temperature < 33:
        status_text = f"☀️ Жегичка ({temperature:.0f}°C / {temperature_f:.0f}°F). Става за плаж и басейн."
    elif temperature < 40:
        status_text = f"🌋 Адска жег ({temperature:.0f}°C / {temperature_f:.0f}°F)! Асфалтът се топи около теб."
    else:
        status_text = f"🔥 Направо пещ ({temperature:.0f}°C / {temperature_f:.0f}°F)! Не може да се живее."
        
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
        <b>🎒 Препоръчителен гардероб:</b><br>{clothes}
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
    h1, h2, h3, h4, h5, h6, p, span, .stMarkdown, .stSubheader {{
        color: #FFFFFF !important;
    }}
    div[data-testid="stWidgetLabel"] p {{
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
    
    if temperature < 10:
        st.session_state.weather_message = f"🥶 Студено е! ({temperature:.1f}°C / {temperature_f:.1f}°F)"
        animation_frames = ["❄️ 🌨️ ❄️", "🌨️ ❄️ 🌨️"]
    elif temperature < 20:
        st.session_state.weather_message = f"🌥️ Прохладно е. ({temperature:.1f}°C / {temperature_f:.1f}°F)"
        animation_frames = ["☁️ 🌤️ ☁️", "🌤️ ☁️ 🌤️"]
    elif temperature < 30:
        st.session_state.weather_message = f"☀️ Приятно топло е! ({temperature:.1f}°C / {temperature_f:.1f}°F)"
        animation_frames = ["🌤️ ☀️ 🌤️", "☀️ 🌤️ ☀️"]
    else:
        st.session_state.weather_message = f"🔥 Много е горещо! ({temperature:.1f}°C / {temperature_f:.1f}°F)"
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
                f"Сега температурата е {temperature} градуса по Целзий ({temperature_f:.1f} градуса по Фаренхайт). "
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
