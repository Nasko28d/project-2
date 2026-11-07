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
if "background_chat" not in st.session_state:
    st.session_state.background_chat = None
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
        "Кой искаш да ти даде официален съвет?",
        ["Грижовната Баба 👵", "Саркастичният Комедиант 🎭", "Професионалният Метеоролог 📊"]
    )
    
    persona_prompts = {
        "Грижовната Баба 👵": "Ти си любяща, но изключително притеснена българска баба. Грижиш се за всички, настояваш за вълнени чорапи и топла супа.",
        "Саркастичният Комедиант 🎭": "Ти си изключително саркастичен и забавен стендъп комедиант, който използва черен хумор и ирония.",
        "Професионалният Метеоролог 📊": "Ти си сериозен, научен метеоролог и климатолог, боравещ само с факти и измервания."
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

# --- ОСНОВЕН ПАНЕЛ: Разделение ---
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
    ai_btn = st.button("Провери с AI & Генерирай фонов чат", type="primary", use_container_width=True)

with info_col:
    # Визуален термометър
    clamped_temp = max(-30.0, min(50.0, temperature))
    percentage = ((clamped_temp + 30) / 80) * 100
    
    if temperature < 5: mercury_color = "#00b4d8"
    elif temperature < 24: mercury_color = "#2a9d8f"
    elif temperature < 33: mercury_color = "#f4a261"
    else: mercury_color = "#e63946"
        
    st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 180px; background: rgba(255,255,255,0.15); border-radius: 15px; padding: 10px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.2);">
            <div style="position: relative; width: 20px; height: 110px; background: #e0e0e0; border-radius: 12px; border: 2px solid #fff; overflow: hidden; display: flex; align-items: flex-end;">
                <div style="width: 100%; height: {percentage}%; background: {mercury_color}; transition: height 0.5s ease;"></div>
            </div>
            <div style="width: 30px; height: 30px; background: {mercury_color}; border-radius: 50%; margin-top: -8px; border: 2px solid #fff;"></div>
            <div style="margin-top: 5px; font-weight: bold; color: white;">{temperature:.1f}°C</div>
        </div>
        """, unsafe_allow_html=True
    )

# --- ГЛОБАЛЕН CSS СТИЛ ---
st.markdown(f"<style>.stApp {{ background-color: {bg_color} !important; }} h1, h2, h3, p, span, label {{ color: white !important; }} .stButton>button {{ border: 2px solid white !important; background: rgba(255,255,255,0.1) !important; color: white !important; }}</style>", unsafe_allow_html=True)

# Проверка на API Ключ
try:
    api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("❌ Липсва GROQ_API_KEY!")
    st.stop()

# --- ЛОГИКА ПРИ НАТИСКАНЕ НА БУТОНА ---
if ai_btn:
    try:
        client = Groq(api_key=api_key)
        
        # 1. ГЕНЕРИРАНЕ НА ФОНОВ ЧАТ (Разговор зад кулисите)
        with st.spinner("🤫 Подслушваме семейния чат зад кулисите..."):
            bg_prompt = (
                f"Напиши кратък, забавен и динамичен скрипт/диалог под формата на групов чат в Viber между трима души: "
                f"1. Баба Станка 👵, 2. Иво Комедианта 🎭, 3. Симеон Метеоролога 📊.\n"
                f"Темата е, че потребителят току-що е задал температура от {temperature}°C.\n"
                f"Всеки трябва да реагира типично за характера си в рамките на 1-2 кратки изречения (общо около 4-5 реплики общо). "
                f"Използвай емоджита и пиши на разговорен български език."
            )
            
            bg_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": bg_prompt}],
                model="llama3-8b-8192",
                temperature=0.8
            )
            st.session_state.background_chat = bg_completion.choices[0].message.content

        # 2. ГЕНЕРИРАНЕ НА ОФИЦИАЛНИЯ СЪВЕТ ОТ ИЗБРАНИЯ ХАРАКТЕР
        with st.spinner(f"🤖 {persona} подготвя официалния си доклад..."):
            prompt = (
                f"Сега температурата е {temperature}°C. Като {persona}, дай съвет в 3 точки:\n"
                f"1. Облекло\n2. Дейност\n3. Здраве\n"
                f"Бъди в пълен синхрон с характера си, пиши на български с много емоджита."
            )
            
            main_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": persona_prompts[persona]},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192",
                temperature=0.7
            )
            st.session_state.current_ai_response = main_completion.choices[0].message.content

    except Exception as e:
        st.error(f"Възникна грешка: {e}")

# --- ИЗВЕЖДАНЕ НА РЕЗУЛТАТИТЕ ---
if st.session_state.background_chat:
    st.markdown("---")
    st.subheader("💬 Фонова дискусия (Какво се случва в общия чат зад гърба ти):")
    # Стилизиран блок за фоновия чат
    st.markdown(
        f"""
        <div style="background: rgba(0, 0, 0, 0.4); padding: 20px; border-radius: 15px; border-left: 5px solid #E91E63; font-family: monospace; white-space: pre-wrap; color: #E0E0E0;">
        {st.session_state.background_chat}
        </div>
        """, unsafe_allow_html=True
    )

if st.session_state.current_ai_response:
    st.markdown("---")
    st.subheader(f"🗣️ Официален съвет от {persona}:")
    st.markdown(st.session_state.current_ai_response)
