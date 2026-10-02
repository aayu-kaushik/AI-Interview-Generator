# app.py



import base64
import textwrap

from pathlib import Path



import streamlit as st



from database import initialize_database, get_interview_history

from services import (
    create_ai_interview,
    load_interview,
    evaluate_answer,
    finalize_interview,
)





# ============================================================

# PAGE CONFIGURATION

# ============================================================



st.set_page_config(

    page_title="AI Interview Generator",

    page_icon="🤖",

    layout="wide",

    initial_sidebar_state="collapsed",

)





# ============================================================

# SETTINGS

# ============================================================



# "overlay" -> robot image fills the whole screen, Welcome card floats on top

# "split"   -> full-page card, robot 50% | Welcome form 50%

WELCOME_LAYOUT = "overlay"





# ============================================================

# PATHS

# ============================================================



BASE_DIR = Path(__file__).resolve().parent



WELCOME_ROBOT = BASE_DIR / "assets" / "welcome_robot.png"

SIDEBAR_ROBOT = BASE_DIR / "assets" / "sidebar_robot.png"





# ============================================================

# DATABASE

# ============================================================



initialize_database()





# ============================================================

# SESSION STATE

# ============================================================



DEFAULT_STATE = {

    "page": "welcome",

    "candidate_name": "",

    "role": "Software Engineer",

    "interview_id": None,

    "interview_data": None,
    "current_question": 0,
    "answers": {},
    "evaluations": {},
    "final_result": None,
}



for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value





# ============================================================

# GLOBAL CSS

# ============================================================



# Matches a column in both old and new Streamlit versions

COL = ':is(div[data-testid="column"], div[data-testid="stColumn"])'



GLOBAL_CSS = """

<style>



/* ---------- Remove Streamlit default UI ---------- */



#MainMenu, footer, header { visibility: hidden; }



[data-testid="stToolbar"],

[data-testid="stDecoration"],

[data-testid="stStatusWidget"],

[data-testid="stImage"] button,

[data-testid="stElementToolbar"],

[data-testid="StyledFullScreenButton"],

button[title="View fullscreen"] { display: none !important; }





/* ---------- Global page ---------- */



html, body, [data-testid="stAppViewContainer"], .stApp {

    background:

        radial-gradient(circle at 82% 8%, rgba(220,239,255,0.85), transparent 34%),

        linear-gradient(135deg, #f8fbff 0%, #eef7ff 100%) !important;

}



html, body, button, input, textarea, select {

    font-family: Inter, "Segoe UI", Arial, sans-serif !important;

}



.block-container {

    max-width: 1400px !important;

    padding: 1.5rem 2rem !important;

}





/* ---------- Inputs ---------- */



.stTextInput label, .stSelectbox label,

.stTextArea label, .stNumberInput label {

    color: #172348 !important;

    font-size: 12px !important;

    font-weight: 700 !important;

}



.stTextInput input, .stNumberInput input {

    min-height: 40px !important;

    border-radius: 7px !important;

    border: 1px solid #d5e1ef !important;

    background: #ffffff !important;

    color: #172348 !important;

    font-size: 13px !important;

}



.stTextInput input::placeholder { color: #9aa8bf !important; }



/* Selectbox: force light look (fixes dark dropdown) */

[data-baseweb="select"],

[data-baseweb="select"] div {

    background: #ffffff !important;

    background-color: #ffffff !important;

    color: #172348 !important;

}



[data-baseweb="select"] > div {

    min-height: 40px !important;

    border-radius: 7px !important;

    border: 1px solid #d5e1ef !important;

    font-size: 13px !important;

}



[data-baseweb="select"] * { color: #172348 !important; }

[data-baseweb="select"] svg { fill: #172348 !important; }



[data-baseweb="popover"] ul,

[data-baseweb="popover"] li,

[data-baseweb="menu"] {

    background: #ffffff !important;

    color: #172348 !important;

}



[data-baseweb="popover"] li:hover { background: #eef6ff !important; }





/* ---------- Buttons (full width) ---------- */



div[data-testid="stElementContainer"]:has(button),

div[data-testid="stButton"],

.stButton {

    width: 100% !important;

}



.stButton button,

div[data-testid="stButton"] button {

    width: 100% !important;

    min-height: 42px !important;

    border: none !important;

    border-radius: 7px !important;

    background: linear-gradient(90deg, #1268ed 0%, #287fff 100%) !important;

    color: #ffffff !important;

    font-size: 13px !important;

    font-weight: 700 !important;

    box-shadow: 0 8px 18px rgba(31,110,235,0.20) !important;

    transition: transform .15s ease, box-shadow .15s ease !important;

}



.stButton button p { color: #ffffff !important; }



.stButton button:hover {

    transform: translateY(-1px);

    box-shadow: 0 10px 24px rgba(31,110,235,0.28) !important;

}





/* ---------- Welcome markers + typography ---------- */



.welcome-page-marker,

.welcome-left-marker,

.welcome-right-marker { display: none; }



.welcome-title {

    color: #0a163a;

    font-size: 30px;

    line-height: 1.1;

    font-weight: 800;

    letter-spacing: -0.5px;

    margin: 0 0 4px 0;

}



.welcome-subtitle {

    color: #172348;

    font-size: 15px;

    font-weight: 700;

    margin-bottom: 6px;

}



.welcome-description {

    color: #71809b;

    font-size: 12px;

    line-height: 1.55;

    margin-bottom: 8px;

}



.welcome-feature { text-align: center; padding: 4px 1px 6px 1px; }



.welcome-feature-icon {

    width: 46px;

    height: 46px;

    display: flex;

    align-items: center;

    justify-content: center;

    margin: 0 auto 8px auto;

    border-radius: 50%;

    background: #eef6ff;

    font-size: 22px;

}



.welcome-feature-title {

    color: #18264a;

    font-size: 12px;

    line-height: 1.35;

    font-weight: 750;

}





/* ---------- Setup page ---------- */



.page-title {

    color: #0b173d;

    font-size: 30px;

    font-weight: 800;

    letter-spacing: -0.5px;

    margin-bottom: 4px;

}



.page-subtitle { color: #6e7c99; font-size: 13px; margin-bottom: 20px; }





/* ---------- Sidebar ---------- */



.sidebar-brand {

    color: #0c193f;

    font-size: 16px;

    line-height: 2.15;

    font-weight: 800;

    margin-bottom: 20px;

}



.sidebar-blue { color: #176ee9; }



.sidebar-active {

    color: #ffffff;

    background: linear-gradient(90deg, #1268ed, #287fff);

    padding: 10px 11px;

    border-radius: 7px;

    font-size: 11px;

    font-weight: 700;

    margin-bottom: 7px;

}



.sidebar-item {

    color: #465371;

    padding: 9px 11px;

    font-size: 11px;

    font-weight: 600;

    margin-bottom: 3px;

}



.sidebar-divider { height: 1px; background: #dce7f3; margin: 20px 3px; }



.sidebar-quote {

    color: #506585;

    font-size: 11px;

    line-height: 1.5;

    text-align: center;

    margin-bottom: 8px;

}





/* ---------- Benefits ---------- */



.benefit-icon { font-size: 24px; }



.benefit-title {

    color: #172348;

    font-size: 12px;

    font-weight: 800;

    margin-bottom: 2px;

}



.benefit-description { color: #75819c; font-size: 10px; line-height: 1.45; }





/* ---------- Ready page ---------- */



.ready-icon { text-align: center; font-size: 52px; margin-top: 80px; }



.ready-title {

    color: #0c193f;

    text-align: center;

    font-size: 29px;

    font-weight: 800;

    margin-top: 7px;

}



.ready-text {

    color: #6e7b98;

    text-align: center;

    font-size: 14px;

    line-height: 1.7;

    margin: 10px auto 25px auto;

    max-width: 600px;

}




/* Functional Interview History navigation styled like the original sidebar item */
.sidebar-history-button-marker {
    display: none;
}

:is(div[data-testid="column"], div[data-testid="stColumn"]):has(.sidebar-brand)
div[data-testid="stElementContainer"]:has(.sidebar-history-button-marker) {
    display: none !important;
}

:is(div[data-testid="column"], div[data-testid="stColumn"]):has(.sidebar-brand)
div[data-testid="stElementContainer"]:has(.sidebar-history-button-marker)
+ div[data-testid="stElementContainer"] .stButton > button {
    width: 100% !important;
    min-height: 52px !important;
    height: auto !important;
    justify-content: center !important;
    background: linear-gradient(135deg,#1677ff 0%,#318cff 100%) !important;
    border: none !important;
    box-shadow: 0 8px 18px rgba(22,119,255,.18) !important;
    padding: 15px 15px !important;
    margin: 0 0 4px 0 !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    text-align: center !important;
}

:is(div[data-testid="column"], div[data-testid="stColumn"]):has(.sidebar-brand)
div[data-testid="stElementContainer"]:has(.sidebar-history-button-marker)
+ div[data-testid="stElementContainer"] .stButton > button p {
    color: #ffffff !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    text-align: center !important;
}

:is(div[data-testid="column"], div[data-testid="stColumn"]):has(.sidebar-brand)
div[data-testid="stElementContainer"]:has(.sidebar-history-button-marker)
+ div[data-testid="stElementContainer"] .stButton > button:hover {
    background: linear-gradient(135deg,#1677ff 0%,#318cff 100%) !important;
    color: #ffffff !important;
    opacity: 1 !important;
}

:is(div[data-testid="column"], div[data-testid="stColumn"]):has(.sidebar-brand)
div[data-testid="stElementContainer"]:has(.sidebar-history-button-marker)
+ div[data-testid="stElementContainer"] .stButton > button:hover p {
    color: #ffffff !important;
}


/* Functional original New Interview navigation */
.sidebar-new-interview-button-marker {
    display: none;
}

:is(div[data-testid="column"], div[data-testid="stColumn"]):has(.sidebar-brand)
div[data-testid="stElementContainer"]:has(.sidebar-new-interview-button-marker) {
    display: none !important;
}

:is(div[data-testid="column"], div[data-testid="stColumn"]):has(.sidebar-brand)
div[data-testid="stElementContainer"]:has(.sidebar-new-interview-button-marker)
+ div[data-testid="stElementContainer"] .stButton > button {
    width: 100% !important;
    min-height: auto !important;
    height: auto !important;
    justify-content: flex-start !important;
    background: linear-gradient(135deg, #1268ed, #338cff) !important;
    border: none !important;
    box-shadow: none !important;
    padding: 14px 15px !important;
    margin: 0 0 8px 0 !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    text-align: left !important;
}

:is(div[data-testid="column"], div[data-testid="stColumn"]):has(.sidebar-brand)
div[data-testid="stElementContainer"]:has(.sidebar-new-interview-button-marker)
+ div[data-testid="stElementContainer"] .stButton > button p {
    color: #ffffff !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    text-align: left !important;
}

:is(div[data-testid="column"], div[data-testid="stColumn"]):has(.sidebar-brand)
div[data-testid="stElementContainer"]:has(.sidebar-new-interview-button-marker)
+ div[data-testid="stElementContainer"] .stButton > button:hover {
    background: linear-gradient(135deg, #0f5fdc, #287eea) !important;
}

</style>

"""



st.markdown(GLOBAL_CSS, unsafe_allow_html=True)





# ============================================================

# WELCOME PAGE CSS (full page)

# ============================================================



# Layout pieces shared by both modes

WELCOME_BASE_CSS = """

body .stApp [data-testid="stMainBlockContainer"],

body .stApp .block-container {

    max-width: 100% !important;

    padding: 0 !important;

}



body [data-testid="stAppViewContainer"],

body [data-testid="stMain"] {

    background: transparent !important;

}



div[data-testid="stHorizontalBlock"]:has(.welcome-left-marker) {

    gap: 0 !important;

    min-height: 100vh !important;

}



__COL__:has(.welcome-right-marker) > div[data-testid="stVerticalBlock"] {

    gap: 0.6rem !important;

    padding: 38px 36px 28px 36px !important;

}

"""



# MODE 1: robot image = full-screen background, Welcome card on top

WELCOME_OVERLAY_CSS = """

body .stApp { background-color: #071329 !important; }



/* Same image for both layers (written once, so the page stays light) */

body .stApp::before,

body .stApp::after {

    content: "";

    position: fixed;

    top: 0;

    pointer-events: none;

    z-index: 0;

    background-image: url('data:image/png;base64,__IMG__');

    background-repeat: no-repeat;

}



/* Layer 1: same picture stretched over the WHOLE screen, softly blurred */

body .stApp::before {

    left: 0;

    width: 100vw;

    height: 100vh;

    background-size: cover;

    background-position: right center;

    filter: blur(26px) brightness(0.6);

    transform: scale(1.12);

}



/* Layer 2: sharp robot image, exactly where it was (left, full height) */

body .stApp::after {

    left: 0;

    height: 100vh;

    aspect-ratio: 1361 / 906;

    background-size: 100% 100%;

    -webkit-mask-image: linear-gradient(to right, #000 86%, transparent 100%);

    mask-image: linear-gradient(to right, #000 86%, transparent 100%);

}



body [data-testid="stAppViewContainer"] {

    position: relative;

    z-index: 1;

}



div[data-testid="stHorizontalBlock"]:has(.welcome-left-marker) {

    align-items: center !important;

}



__COL__:has(.welcome-left-marker) {

    flex: 1 1 auto !important;

    min-width: 0 !important;

}



__COL__:has(.welcome-right-marker) {

    flex: 0 0 34% !important;

    width: 34% !important;

    min-width: 400px !important;

    margin-right: 5vw !important;

    min-height: 70vh !important;

    background: #ffffff !important;

    border-radius: 20px !important;

    box-shadow: 0 25px 60px rgba(0,0,0,0.38) !important;

}



__COL__:has(.welcome-right-marker) > div[data-testid="stVerticalBlock"] {

    min-height: 70vh !important;

    box-sizing: border-box !important;

    justify-content: flex-start !important;

    gap: 1.05rem !important;

    padding: 30px 36px 38px 36px !important;

}



/* Features row: pinned to the bottom of the card with a thin divider */

__COL__:has(.welcome-right-marker) > div[data-testid="stVerticalBlock"] > div:last-child {

    margin-top: auto !important;

    padding-top: 20px !important;

    padding-bottom: 4px !important;

    border-top: 1px solid #e6eef8 !important;

}



@media (max-width: 900px) {

    body .stApp::after {

        width: 100vw;

        aspect-ratio: auto;

        background-size: cover;

        background-position: center;

        -webkit-mask-image: none;

        mask-image: none;

    }



    div[data-testid="stHorizontalBlock"]:has(.welcome-left-marker) {

        display: block !important;

        padding: 4vw 0 !important;

    }



    __COL__:has(.welcome-left-marker) { display: none !important; }



    __COL__:has(.welcome-right-marker) {

        width: 92% !important;

        min-width: 0 !important;

        margin: 0 auto !important;

    }

}

"""



# MODE 2: full-page card, robot 50% | form 50%

WELCOME_SPLIT_CSS = """

body .stApp { background: #ffffff !important; }



div[data-testid="stHorizontalBlock"]:has(.welcome-left-marker) {

    align-items: stretch !important;

}



__COL__:has(.welcome-left-marker) {

    flex: 0 0 50% !important;

    width: 50% !important;

    min-width: 50% !important;

    background-color: #071329 !important;

    background-image: url('data:image/png;base64,__IMG__') !important;

    background-size: cover !important;

    background-position: center !important;

    background-repeat: no-repeat !important;

}



__COL__:has(.welcome-right-marker) {

    flex: 0 0 50% !important;

    width: 50% !important;

    min-width: 50% !important;

    background: #ffffff !important;

}



__COL__:has(.welcome-right-marker) > div[data-testid="stVerticalBlock"] {

    height: 100% !important;

    justify-content: center !important;

    padding: 40px 9% !important;

}



@media (max-width: 900px) {

    div[data-testid="stHorizontalBlock"]:has(.welcome-left-marker) {

        display: block !important;

    }



    __COL__:has(.welcome-left-marker),

    __COL__:has(.welcome-right-marker) {

        width: 100% !important;

        min-width: 100% !important;

    }



    __COL__:has(.welcome-left-marker) { min-height: 260px !important; }

}

"""






# Keep validation/warning messages readable across all pages.
st.markdown(
    """
    <style>
    div[data-testid="stAlert"][data-baseweb="notification"],
    div[data-testid="stAlert"] {
        opacity: 1 !important;
    }

    div[data-testid="stAlert"] > div,
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span,
    div[data-testid="stAlert"] div {
        color: #5f4b00 !important;
        opacity: 1 !important;
        font-weight: 600 !important;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def build_welcome_css(encoded_image):

    mode_css = (

        WELCOME_SPLIT_CSS

        if WELCOME_LAYOUT == "split"

        else WELCOME_OVERLAY_CSS

    )



    css = "<style>" + WELCOME_BASE_CSS + mode_css + "</style>"



    return (

        css

        .replace("__COL__", COL)

        .replace("__IMG__", encoded_image)

    )





# ============================================================

# SETUP PAGE CSS (full screen + larger sizes)

# ============================================================



SETUP_CSS = """

<style>



.setup-page-marker { display: none; }



/* Full screen width */

[data-testid="stMainBlockContainer"]:has(.setup-page-marker),

.block-container:has(.setup-page-marker) {

    max-width: 100% !important;

    padding: 0.6rem 3.5rem 1rem 3.5rem !important;

}



/* Invisible helper blocks (CSS + marker) were adding empty gaps at the top */

__S__ div[data-testid="stElementContainer"]:has(style),

__S__ div[data-testid="stElementContainer"]:has(.setup-page-marker) {

    display: none !important;

}



/* Titles */

__S__ .page-title { font-size: 42px; }

__S__ .page-subtitle { font-size: 17px; margin-bottom: 30px; }



/* Labels */

__S__ [data-testid="stWidgetLabel"] p,

__S__ .stTextInput label,

__S__ .stSelectbox label {

    font-size: 15px !important;

}



/* Inputs + dropdowns */

__S__ .stTextInput input {

    min-height: 52px !important;

    font-size: 16px !important;

}



__S__ [data-baseweb="select"] > div {

    min-height: 52px !important;

    font-size: 16px !important;

}



__S__ [data-baseweb="select"] * { font-size: 16px !important; }



/* Buttons */

__S__ .stButton button {

    min-height: 54px !important;

    font-size: 16px !important;

}



__S__ .stButton button p { font-size: 16px !important; }



/* Sidebar */

__S__ .sidebar-brand { font-size: 25px; margin-bottom: 26px; }



__S__ .sidebar-active {

    font-size: 15px;

    padding: 14px 15px;

    margin-bottom: 8px;

}



__S__ .sidebar-item {

    font-size: 15px;

    padding: 12px 15px;

    margin-bottom: 4px;

}



__S__ .sidebar-quote { font-size: 15px; }



/* Benefits (right side) */

__S__ .benefit-icon { font-size: 46px; line-height: 1.1; }

__S__ .benefit-title { font-size: 19px; margin-bottom: 4px; }

__S__ .benefit-description { font-size: 15px; line-height: 1.5; }



/* Benefit cards: lift slightly on hover */

__S__ div[data-testid="stHorizontalBlock"]:has(.benefit-icon) {

    align-items: center !important;

    padding: 14px 20px !important;

    background: rgba(255,255,255,0.65);

    border: 1px solid #dbe8f6;

    border-radius: 16px;

    transition:

        transform .2s ease,

        box-shadow .2s ease,

        background .2s ease,

        border-color .2s ease;

}



__S__ div[data-testid="stHorizontalBlock"]:has(.benefit-icon):hover {

    transform: translateY(-5px);

    background: #ffffff;

    border-color: #9cc4f5;

    box-shadow: 0 14px 30px rgba(31,110,235,0.16);

}



/* Dark left sidebar: the whole column (robot sits on black) */

__S__ __COL__:has(.sidebar-brand) {

    background:

        radial-gradient(circle at 50% 72%, rgba(40,127,255,0.30), transparent 58%),

        linear-gradient(180deg, #0b1838 0%, #040a18 100%) !important;

    border-radius: 18px !important;

    padding: 26px 18px 22px 18px !important;

    box-shadow: 0 16px 36px rgba(4,10,24,0.35) !important;

}



__S__ .sidebar-brand { color: #ffffff; }

__S__ .sidebar-blue { color: #4da3ff; }



__S__ .sidebar-item {

    color: #b9c7e2;

    border-radius: 7px;

    transition: background .2s ease, color .2s ease;

}



__S__ .sidebar-item:hover {

    background: rgba(255,255,255,0.08);

    color: #ffffff;

}



__S__ .sidebar-divider { background: rgba(255,255,255,0.14); }

__S__ .sidebar-quote { color: #b9c7e2; }



</style>

""".replace("__COL__", COL).replace("__S__", ".stApp:has(.setup-page-marker)")





# ============================================================
# INTERVIEW PAGE CSS
# ============================================================

INTERVIEW_CSS = """
<style>
.interview-page-marker { display:none; }
.stApp:has(.interview-page-marker) [data-testid="stMainBlockContainer"], .stApp:has(.interview-page-marker) .block-container { max-width:100% !important; padding:0.6rem 3.5rem 1rem 3.5rem !important; }
.stApp:has(.interview-page-marker) div[data-testid="stElementContainer"]:has(.interview-page-marker) { display:none !important; }
.stApp:has(.interview-page-marker) __COL__:has(.sidebar-brand) { background:radial-gradient(circle at 50% 72%,rgba(40,127,255,.30),transparent 58%),linear-gradient(180deg,#0b1838 0%,#040a18 100%) !important; border-radius:18px !important; padding:26px 18px 22px 18px !important; box-shadow:0 16px 36px rgba(4,10,24,.35) !important; }
.stApp:has(.interview-page-marker) .sidebar-brand { color:#fff; font-size:25px; margin-bottom:26px; }
.stApp:has(.interview-page-marker) .sidebar-blue { color:#4da3ff; }
.stApp:has(.interview-page-marker) .sidebar-active { font-size:15px; padding:14px 15px; margin-bottom:8px; }
.stApp:has(.interview-page-marker) .sidebar-item { color:#b9c7e2; font-size:15px; padding:12px 15px; margin-bottom:4px; border-radius:7px; }
.stApp:has(.interview-page-marker) .sidebar-divider { background:rgba(255,255,255,.14); }
.stApp:has(.interview-page-marker) .sidebar-quote { color:#b9c7e2; font-size:15px; }
.interview-title { color:#0b173d; font-size:35px; line-height:1.15; font-weight:800; letter-spacing:-.6px; margin-bottom:6px; }
.interview-meta { color:#71809b; font-size:15px; font-weight:600; margin-bottom:22px; }
.candidate-card { background:#fff; border:1px solid #dce8f5; border-radius:16px; padding:22px; box-shadow:0 8px 24px rgba(31,75,125,.08); margin-bottom:18px; }
.candidate-card-title { color:#0b173d; font-size:17px; font-weight:800; margin-bottom:16px; }
.candidate-label { color:#8b98ad; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.5px; margin-top:10px; }
.candidate-value { color:#263454; font-size:14px; font-weight:650; margin-top:2px; }
.question-progress-top { display:flex; justify-content:space-between; align-items:center; margin-bottom:9px; }
.question-counter { color:#172348; font-size:15px; font-weight:800; }
.question-percentage { color:#176ee9; font-size:14px; font-weight:800; }
.question-progress-track { width:100%; height:9px; border-radius:20px; overflow:hidden; background:#dfe9f5; margin-bottom:22px; }
.question-progress-fill { height:100%; border-radius:20px; background:linear-gradient(90deg,#1268ed,#47a0ff); }
.question-card { position:relative; overflow:hidden; background:linear-gradient(135deg,#fff 0%,#f4f9ff 100%); border:1px solid #d9e7f5; border-radius:18px; padding:28px 30px; box-shadow:0 12px 30px rgba(31,75,125,.09); margin-bottom:22px; }
.question-card::before { content:""; position:absolute; left:0; top:0; bottom:0; width:5px; background:linear-gradient(180deg,#1268ed,#4ca7ff); }
.question-number { color:#176ee9; font-size:12px; font-weight:800; letter-spacing:1.1px; margin-bottom:12px; }
.question-text { color:#111f43; font-size:20px; line-height:1.55; font-weight:700; }
.answer-heading { color:#172348; font-size:16px; font-weight:800; margin-bottom:7px; }
.answer-help { color:#8491a8; font-size:12px; margin-bottom:8px; }
.stApp:has(.interview-page-marker) .stTextArea textarea { min-height:190px !important; background:#fff !important; color:#172348 !important; border:1px solid #d5e1ef !important; border-radius:13px !important; padding:15px !important; font-size:15px !important; line-height:1.55 !important; }
.stApp:has(.interview-page-marker) .stButton button { min-height:50px !important; font-size:15px !important; }
.stApp:has(.interview-page-marker) button[kind="secondary"] { background:#fff !important; color:#344563 !important; border:1px solid #d5e1ef !important; box-shadow:none !important; }
.stApp:has(.interview-page-marker) button[kind="secondary"] p { color:#344563 !important; }
.interview-tip { background:rgba(234,245,255,.85); border:1px solid #d6e9fb; border-radius:13px; padding:15px; color:#526582; font-size:12px; line-height:1.55; margin-top:14px; }
</style>
""".replace("__COL__", COL)


RESULTS_CSS = """
<style>
.results-page-marker{display:none}.stApp:has(.results-page-marker) [data-testid="stMainBlockContainer"],.stApp:has(.results-page-marker) .block-container{max-width:100%!important;padding:.6rem 3.5rem 2rem!important}.stApp:has(.results-page-marker) __COL__:has(.sidebar-brand){background:radial-gradient(circle at 50% 72%,rgba(40,127,255,.30),transparent 58%),linear-gradient(180deg,#0b1838,#040a18)!important;border-radius:18px!important;padding:26px 18px 22px!important;box-shadow:0 16px 36px rgba(4,10,24,.35)!important}.stApp:has(.results-page-marker) .sidebar-brand{color:#fff;font-size:25px}.stApp:has(.results-page-marker) .sidebar-blue{color:#4da3ff}.stApp:has(.results-page-marker) .sidebar-item,.stApp:has(.results-page-marker) .sidebar-quote{color:#b9c7e2}.results-title{color:#0b173d;font-size:36px;font-weight:800;margin-bottom:7px}.results-subtitle{color:#71809b;font-size:15px;margin-bottom:22px}.results-hero{background:linear-gradient(135deg,#0d6efd,#49a4ff);border-radius:20px;padding:28px 30px;color:#fff;box-shadow:0 14px 34px rgba(25,112,235,.22);margin-bottom:22px}.results-hero-small{font-size:13px;font-weight:700;opacity:.88;text-transform:uppercase}.results-score{font-size:46px;font-weight:850;margin:8px 0}.results-performance{font-size:17px;font-weight:700}.results-card{background:#fff;border:1px solid #dce8f5;border-radius:16px;padding:20px 22px;box-shadow:0 8px 24px rgba(31,75,125,.07);margin-bottom:16px}.results-card-label{color:#8593aa;font-size:11px;font-weight:800;text-transform:uppercase}.results-card-value{color:#15244a;font-size:22px;font-weight:800}.results-section-title{color:#0b173d;font-size:23px;font-weight:800;margin:25px 0 13px}.result-question-card{background:#fff;border:1px solid #dce8f5;border-radius:17px;padding:22px 24px;box-shadow:0 8px 24px rgba(31,75,125,.07);margin-bottom:17px}.result-q-number{color:#176ee9;font-size:12px;font-weight:850;letter-spacing:1px;margin-bottom:8px}.result-q-text{color:#142348;font-size:17px;line-height:1.5;font-weight:750;margin-bottom:16px}.result-chip{display:inline-block;background:#eaf4ff;color:#176ee9;border-radius:999px;padding:7px 12px;font-size:12px;font-weight:800;margin-bottom:15px}.result-block{background:#f7faff;border:1px solid #e2ebf5;border-radius:12px;padding:14px 16px;margin-top:10px}.result-block-title{color:#526582;font-size:11px;font-weight:850;text-transform:uppercase;margin-bottom:5px}.result-block-text{color:#263454;font-size:14px;line-height:1.55;white-space:pre-wrap}.stApp:has(.results-page-marker) .stButton button{min-height:49px!important}

/* Keep the PDF download button solid black in every interaction state. */
.stApp:has(.results-page-marker) div[data-testid="stDownloadButton"] {
    width: 100% !important;
}

.stApp:has(.results-page-marker) div[data-testid="stDownloadButton"] > button,
.stApp:has(.results-page-marker) div[data-testid="stDownloadButton"] > button:hover,
.stApp:has(.results-page-marker) div[data-testid="stDownloadButton"] > button:focus,
.stApp:has(.results-page-marker) div[data-testid="stDownloadButton"] > button:focus-visible,
.stApp:has(.results-page-marker) div[data-testid="stDownloadButton"] > button:active,
.stApp:has(.results-page-marker) div[data-testid="stDownloadButton"] > button:disabled,
.stApp:has(.results-page-marker) div[data-testid="stDownloadButton"] > button[disabled] {
    width: 100% !important;
    min-height: 49px !important;
    background: #111722 !important;
    background-color: #111722 !important;
    color: #ffffff !important;
    border: none !important;
    opacity: 1 !important;
    filter: none !important;
    box-shadow: none !important;
    transform: none !important;
    cursor: pointer !important;
}

.stApp:has(.results-page-marker) div[data-testid="stDownloadButton"] > button *,
.stApp:has(.results-page-marker) div[data-testid="stDownloadButton"] > button:hover *,
.stApp:has(.results-page-marker) div[data-testid="stDownloadButton"] > button:focus *,
.stApp:has(.results-page-marker) div[data-testid="stDownloadButton"] > button:active *,
.stApp:has(.results-page-marker) div[data-testid="stDownloadButton"] > button:disabled * {
    color: #ffffff !important;
    opacity: 1 !important;
}


/* Existing About sidebar navigation, now functional */
.sidebar-about-button-marker + div[data-testid="stButton"] button {
    width: 100% !important;
    justify-content: flex-start !important;
    min-height: 42px !important;
    padding: 0 12px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #b8c5dc !important;
    font-weight: 600 !important;
}
.sidebar-about-button-marker + div[data-testid="stButton"] button:hover,
.sidebar-about-button-marker + div[data-testid="stButton"] button:focus,
.sidebar-about-button-marker + div[data-testid="stButton"] button:active {
    background: rgba(255,255,255,0.06) !important;
    color: #ffffff !important;
    border: none !important;
    opacity: 1 !important;
}
.sidebar-about-button-marker + div[data-testid="stButton"] button p {
    color: inherit !important;
}

/* About page */
.about-page-marker { display:none; }

/* Force readable About-page colors over the app's global text rules. */
.about-hero,
.about-hero h1,
.about-hero h2,
.about-hero h3,
.about-hero h4,
.about-hero p,
.about-hero span {
    color: #ffffff !important;
}

.about-section,
.about-card {
    color: #102447 !important;
}

.about-section h1,
.about-section h2,
.about-section h3,
.about-section h4,
.about-card h1,
.about-card h2,
.about-card h3,
.about-card h4 {
    color: #102447 !important;
}

.about-section p,
.about-card p {
    color: #53647e !important;
}

.about-step {
    color: #23436f !important;
}

.about-pill {
    color: #1769d2 !important;
}

.about-footer {
    color: #8190a7 !important;
}
.stApp:has(.about-page-marker) .block-container {
    max-width: 1180px !important;
    padding-top: 2.1rem !important;
    padding-bottom: 3rem !important;
}
.about-hero {
    background: linear-gradient(135deg, #1677ff 0%, #4b9cff 100%);
    border-radius: 24px;
    padding: 38px 42px;
    color: white;
    box-shadow: 0 16px 38px rgba(28,105,220,.18);
    margin-bottom: 24px;
}
.about-hero h1 { margin:0 0 8px; font-size:2.25rem; color:white; }
.about-hero p { margin:0; font-size:1.03rem; line-height:1.7; color:rgba(255,255,255,.94); }
.about-section {
    background:#fff; border:1px solid #e2eaf5; border-radius:20px;
    padding:26px 28px; margin:16px 0; box-shadow:0 8px 24px rgba(20,56,105,.06);
}
.about-section h3 { margin:0 0 12px; color:#102447; }
.about-section p { margin:0; color:#53647e; line-height:1.75; }
.about-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; margin:16px 0; }
.about-card { background:#f7faff; border:1px solid #e1eaf7; border-radius:18px; padding:21px; }
.about-card h4 { margin:0 0 8px; color:#15315d; font-size:1rem; }
.about-card p { margin:0; color:#61718a; line-height:1.65; font-size:.94rem; }
.about-flow { display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-top:18px; }
.about-step {
    flex:1 1 145px; background:#f6f9fe; border:1px solid #dfe8f5;
    border-radius:14px; padding:14px 12px; text-align:center; font-weight:700; color:#23436f;
}
.about-tech { display:flex; flex-wrap:wrap; gap:10px; margin-top:14px; }
.about-pill {
    background:#edf5ff; color:#1769d2; border:1px solid #d7e9ff;
    border-radius:999px; padding:8px 14px; font-weight:700; font-size:.9rem;
}
.about-footer { text-align:center; color:#8190a7; padding:20px 0 4px; font-size:.9rem; }
@media (max-width:850px) {
    .about-grid { grid-template-columns:1fr; }
    .about-hero { padding:30px 25px; }
}

/* ============================================================
   RESULTS PAGE - STICKY LEFT SIDEBAR
   ============================================================ */

.stApp:has(.results-page-marker)
:is(div[data-testid="column"], div[data-testid="stColumn"]):has(.sidebar-brand) {
    position: sticky !important;
    top: 10px !important;
    align-self: flex-start !important;
    height: calc(100vh - 20px) !important;
    max-height: calc(100vh - 20px) !important;
    overflow: hidden !important;
    z-index: 50 !important;
}

</style>
""".replace("__COL__", COL)


# ============================================================

# HELPERS

# ============================================================




# ============================================================
# INTERVIEW HISTORY PAGE CSS
# ============================================================

HISTORY_CSS = """
<style>
.history-page-marker { display:none; }

.stApp:has(.history-page-marker) [data-testid="stMainBlockContainer"],
.stApp:has(.history-page-marker) .block-container {
    max-width:100% !important;
    padding:0.6rem 3.5rem 1rem 3.5rem !important;
}

.stApp:has(.history-page-marker)
:is(div[data-testid="column"], div[data-testid="stColumn"]):has(.sidebar-brand) {
    position:sticky !important;
    top:10px !important;
    align-self:flex-start !important;
    height:calc(100vh - 20px) !important;
    max-height:calc(100vh - 20px) !important;
    overflow:hidden !important;
    z-index:50 !important;
    background:
        radial-gradient(circle at 50% 72%, rgba(40,127,255,0.30), transparent 58%),
        linear-gradient(180deg,#0b1838 0%,#040a18 100%) !important;
    border-radius:18px !important;
    padding:26px 18px 22px 18px !important;
    box-shadow:0 16px 36px rgba(4,10,24,0.35) !important;
}

.history-title {
    color:#0b173d; font-size:35px; line-height:1.15; font-weight:800;
    letter-spacing:-0.6px; margin-bottom:6px;
}
.history-subtitle {
    color:#71809b; font-size:15px; font-weight:500; margin-bottom:24px;
}
.history-summary-card {
    background:linear-gradient(135deg,#1268ed 0%,#48a1ff 100%);
    border-radius:18px; padding:22px 26px; color:white;
    box-shadow:0 14px 34px rgba(18,104,237,0.20); margin-bottom:24px;
}
.history-summary-small {
    font-size:12px; font-weight:800; text-transform:uppercase;
    letter-spacing:.7px; opacity:.9;
}
.history-summary-value { font-size:31px; font-weight:800; margin-top:5px; }

.history-card {
    background:#fff; border:1px solid #dce8f5; border-radius:17px;
    padding:22px 24px; box-shadow:0 9px 25px rgba(31,75,125,.08);
    margin-bottom:12px;
}
.history-role { color:#0b173d; font-size:20px; font-weight:800; margin-bottom:4px; }
.history-date { color:#8290a8; font-size:12px; font-weight:600; margin-bottom:15px; }

.history-grid {
    display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:12px;
}
.history-field {
    background:#f5f9fe; border:1px solid #e1ebf6; border-radius:11px;
    padding:11px 12px;
}
.history-label {
    color:#8290a8; font-size:10px; font-weight:800; text-transform:uppercase;
    letter-spacing:.5px; margin-bottom:4px;
}
.history-value {
    color:#1b2948; font-size:13px; font-weight:700; word-break:break-word;
}
.history-status-completed { color:#157347; }
.history-status-progress { color:#a96a00; }

.history-empty {
    background:#fff; border:1px dashed #c9d9ea; border-radius:18px;
    padding:55px 30px; text-align:center; color:#71809b; margin-top:20px;
}
.history-empty-icon { font-size:44px; margin-bottom:10px; }
.history-empty-title {
    color:#0b173d; font-size:21px; font-weight:800; margin-bottom:6px;
}

@media (max-width:1100px) {
    .history-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
}
</style>
"""


def html_block(css_class, content):

    st.markdown(

        f'<div class="{css_class}">{content}</div>',

        unsafe_allow_html=True,

    )





def go_to(page_name):

    st.session_state.page = page_name

    st.rerun()





def image_to_base64(path):

    return base64.b64encode(path.read_bytes()).decode()





# Set to False to show the sidebar robot exactly as the original picture

SIDEBAR_ROBOT_TRANSPARENT = True





@st.cache_data(show_spinner=False)

def sidebar_robot_base64():

    """Sidebar robot with its white background removed (shows the dark sidebar)."""



    if not SIDEBAR_ROBOT_TRANSPARENT:

        return image_to_base64(SIDEBAR_ROBOT)



    try:

        import io



        import numpy as np

        from PIL import Image, ImageDraw, ImageFilter



        picture = Image.open(SIDEBAR_ROBOT).convert("RGBA")



        white = Image.new("RGBA", picture.size, (255, 255, 255, 255))

        white.alpha_composite(picture)



        work = white.convert("RGB")

        width, height = work.size

        marker = (255, 0, 255)



        # Fill the white background starting from the 4 corners only,

        # so the white parts of the robot itself are untouched.

        for corner in [(0, 0), (width - 1, 0),

                       (0, height - 1), (width - 1, height - 1)]:

            if work.getpixel(corner) != marker:

                ImageDraw.floodfill(work, corner, marker, thresh=38)



        background = (np.array(work) == marker).all(axis=2)

        alpha = np.where(background, 0, 255).astype("uint8")

        alpha = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(1.2))



        result = white.convert("RGB").convert("RGBA")

        result.putalpha(alpha)



        buffer = io.BytesIO()

        result.save(buffer, format="PNG")



        return base64.b64encode(buffer.getvalue()).decode()



    except Exception:

        return image_to_base64(SIDEBAR_ROBOT)





def welcome_feature(icon, title):

    st.markdown(

        (

            '<div class="welcome-feature">'

            f'<div class="welcome-feature-icon">{icon}</div>'

            f'<div class="welcome-feature-title">{title}</div>'

            "</div>"

        ),

        unsafe_allow_html=True,

    )





def benefit(icon, title, description):

    icon_column, text_column = st.columns([0.2, 0.8], gap="small")



    with icon_column:

        html_block("benefit-icon", icon)



    with text_column:

        html_block("benefit-title", title)

        html_block("benefit-description", description)





# ============================================================

# WELCOME PAGE

# ============================================================



def show_welcome():



    st.markdown(

        '<div class="welcome-page-marker"></div>',

        unsafe_allow_html=True,

    )



    if WELCOME_ROBOT.exists():

        st.markdown(

            build_welcome_css(image_to_base64(WELCOME_ROBOT)),

            unsafe_allow_html=True,

        )

    else:

        st.error("assets/welcome_robot.png was not found.")



    robot_column, form_column = st.columns([0.5, 0.5], gap="small")



    # ---------------- LEFT SIDE (image comes from CSS) ----------------



    with robot_column:

        st.markdown(

            '<div class="welcome-left-marker"></div>',

            unsafe_allow_html=True,

        )



    # ---------------- RIGHT SIDE ----------------



    with form_column:



        st.markdown(

            '<div class="welcome-right-marker"></div>',

            unsafe_allow_html=True,

        )



        html_block("welcome-title", "Welcome 👋")

        html_block("welcome-subtitle", "Let's get you started")

        html_block(

            "welcome-description",

            (

                "Create AI-powered mock interviews with "

                "personalized questions and detailed feedback."

            ),

        )



        candidate_name = st.text_input(

            "Your Name",

            value=st.session_state.candidate_name,

            placeholder="Enter your name",

            key="welcome_candidate_name",

        )



        role_options = [

            "Software Engineer",

            "AI Engineer",

            "Machine Learning Engineer",

            "Data Scientist",

            "Data Analyst",

            "Python Developer",

            "Backend Developer",

            "Frontend Developer",

            "Full Stack Developer",

            "Web Developer",

            "Network Engineer",

            "Cybersecurity Analyst",

            "Cloud Engineer",

            "Other",

        ]



        saved_role = st.session_state.role

        role_index = (

            role_options.index(saved_role)

            if saved_role in role_options

            else 0

        )



        selected_role = st.selectbox(

            "Job Role",

            role_options,

            index=role_index,

            key="welcome_job_role",

        )



        custom_role = ""



        if selected_role == "Other":

            custom_role = st.text_input(

                "Custom Job Role",

                placeholder="Enter your job role",

                key="welcome_custom_job_role",

            )



        if st.button("Get Started  →", key="welcome_start_button"):



            final_role = (

                custom_role.strip()

                if selected_role == "Other"

                else selected_role

            )



            if not candidate_name.strip():

                st.warning("⚠ Please enter your name to continue.")



            elif not final_role:

                st.warning("Please enter your job role.")



            else:

                st.session_state.candidate_name = candidate_name.strip()

                st.session_state.role = final_role

                go_to("setup")



        feature_1, feature_2, feature_3 = st.columns(3)



        with feature_1:

            welcome_feature("💡", "AI Generated<br>Questions")



        with feature_2:

            welcome_feature("📋", "Detailed<br>Evaluation")



        with feature_3:

            welcome_feature("📈", "Personalized<br>Feedback")





# ============================================================

# DASHBOARD SIDEBAR

# ============================================================



def show_sidebar():
    st.markdown(SIDEBAR_HISTORY_BLUE_CSS, unsafe_allow_html=True)



    with st.container():



        html_block(

            "sidebar-brand",

            (

                "AI Interview<br>"

                '<span class="sidebar-blue">Generator</span>'

            ),

        )



        st.markdown(
            '<div class="sidebar-new-interview-button-marker"></div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "🏠  New Interview",
            key="sidebar_new_interview_nav",
        ):
            st.session_state.current_question = 0
            st.session_state.answers = {}
            st.session_state.evaluations = {}
            st.session_state.final_result = None
            st.session_state.interview_id = None
            st.session_state.interview_data = None
            go_to("setup")

        st.markdown(
            '<div class="sidebar-history-button-marker"></div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "◷  Interview History",
            key="sidebar_history_nav",
            type="secondary",
        ):
            go_to("history")

        st.markdown('<div class="sidebar-about-button-marker"></div>', unsafe_allow_html=True)
        if st.button("ⓘ  About", key="sidebar_about_nav", type="secondary"):
            go_to("about")

        html_block("sidebar-divider", "")

        html_block(

            "sidebar-quote",

            '"Practice Smarter<br>with AI"',

        )



        if SIDEBAR_ROBOT.exists():

            st.markdown(

                (

                    '<img src="data:image/png;base64,'

                    + sidebar_robot_base64()

                    + '" style="width:100%;display:block;">'

                ),

                unsafe_allow_html=True,

            )





# ============================================================

# INTERVIEW SETUP PAGE


# ============================================================



def show_setup():



    st.markdown(

        '<div class="setup-page-marker"></div>',

        unsafe_allow_html=True,

    )

    st.markdown(SETUP_CSS, unsafe_allow_html=True)



    sidebar_column, main_column = st.columns([0.19, 0.81], gap="large")



    with sidebar_column:



        show_sidebar()



        st.write("")



        if st.button("← Back", key="setup_back_button"):

            go_to("welcome")



    with main_column:



        html_block("page-title", "Create Your AI Interview")



        html_block(

            "page-subtitle",

            (

                "Get personalized interview questions "

                "with AI-powered evaluation and "

                "detailed feedback."

            ),

        )



        form_column, benefits_column = st.columns(

            [0.65, 0.35],

            gap="large",

        )



        # ---------------- FORM ----------------



        with form_column:



            candidate_name = st.text_input(

                "Candidate Name",

                value=st.session_state.candidate_name,

                key="setup_candidate_name",

            )



            role = st.text_input(

                "Job Role",

                value=st.session_state.role,

                key="setup_job_role",

            )



            skills = st.text_input(

                "Skills (comma separated)",

                placeholder="Python, SQL, DSA, System Design",

                key="setup_skills",

            )



            experience_column, difficulty_column = st.columns(2)



            with experience_column:

                experience = st.selectbox(

                    "Experience Level",

                    ["Fresher", "0-1 Years", "1-3 Years",

                     "3-5 Years", "5+ Years"],

                    key="setup_experience",

                )



            with difficulty_column:

                difficulty = st.selectbox(

                    "Difficulty Level",

                    ["Easy", "Medium", "Hard"],

                    index=1,

                    key="setup_difficulty",

                )



            type_column, number_column = st.columns(2)



            with type_column:

                interview_type = st.selectbox(

                    "Interview Type",

                    ["Technical", "HR", "Behavioral", "Mixed"],

                    key="setup_interview_type",

                )



            with number_column:

                number_of_questions = st.selectbox(

                    "Number of Questions",

                    [3, 5, 7, 10],

                    index=1,

                    key="setup_question_count",

                )



            st.write("")



            if st.button("▶  Start AI Interview", key="setup_start_button"):



                if not candidate_name.strip():

                    st.warning("Candidate name is required.")



                elif not role.strip():

                    st.warning("Job role is required.")



                elif not skills.strip():

                    st.warning("⚠ Please enter at least one skill before starting the interview.")



                else:

                    st.session_state.candidate_name = candidate_name.strip()

                    st.session_state.role = role.strip()



                    loading_box = st.empty()

                    # Use native Streamlit markup here instead of nested HTML.
                    # This avoids Markdown interpreting any <div> content as a code block.
                    loading_box.info(
                        "✦  Preparing Your AI Interview...\n\n"
                        f"Gemini is creating a personalized interview for {candidate_name.strip()}.\n\n"
                        "✓  Analyzing role, skills & experience\n\n"
                        "✦  Generating personalized questions\n\n"
                        "◈  Creating evaluation rubrics\n\n"
                        "⏳  Finalizing your interview\n\n"
                        "This may take a few moments. Please keep this page open."
                    )

                    try:
                        with st.spinner("Generating questions and evaluation rubrics..."):
                            result = create_ai_interview(

                                candidate_name=candidate_name.strip(),

                                role=role.strip(),

                                skills=skills.strip(),

                                experience=experience,

                                difficulty=difficulty,

                                interview_type=interview_type,

                                number_of_questions=number_of_questions,

                            )
                    except Exception:
                        result = {
                            "success": False,
                            "message": (
                                "We couldn't prepare the interview right now. "
                                "Please check your internet/API configuration and try again."
                            ),
                        }
                    finally:
                        loading_box.empty()



                    if result.get("success"):

                        st.session_state.interview_id = result.get(

                            "interview_id"

                        )

                        st.session_state.interview_data = result

                        go_to("generated")



                    else:

                        st.error(

                            result.get(

                                "message",

                                "Interview generation failed.",

                            )

                        )



        # ---------------- BENEFITS ----------------



        with benefits_column:



            st.write("")

            st.write("")



            benefit(

                "💡",

                "AI Generated Questions",

                "Tailored to your role, skills and experience.",

            )



            benefit(

                "📋",

                "Detailed Evaluation",

                "Rubric-based scoring for every candidate answer.",

            )



            benefit(

                "📈",

                "Personalized Feedback",

                "Identify strengths and areas for improvement.",

            )



            benefit(

                "🎯",

                "Real Interview Practice",

                "Build confidence through realistic interview practice.",

            )



            benefit(

                "🏆",

                "Track Your Progress",

                "Review past interviews and watch your scores improve.",

            )





# ============================================================
# TEMPORARY READY PAGE
# ============================================================

def show_generated():
    result = st.session_state.interview_data
    if not result:
        go_to("welcome")
        return

    questions_created = result.get("questions_created", 0)
    html_block("ready-icon", "✨")
    html_block("ready-title", "Your AI Interview is Ready!")
    html_block("ready-text", f"{questions_created} interview questions and their hidden evaluation rubrics have been generated successfully.")
    left, center, right = st.columns([1, 0.7, 1])

    with center:
        if st.button("Start Interview  →", key="ready_start_button"):
            st.session_state.current_question = 0
            st.session_state.answers = {}
            st.session_state.evaluations = {}
            st.session_state.final_result = None
            go_to("interview")

        if st.button("← Create Another Interview", key="ready_back_button"):
            go_to("setup")


# ============================================================
# ACTUAL INTERVIEW PAGE
# ============================================================

def show_interview():
    st.markdown('<div class="interview-page-marker"></div>', unsafe_allow_html=True)
    st.markdown(INTERVIEW_CSS, unsafe_allow_html=True)

    interview_id = st.session_state.interview_id
    if not interview_id:
        st.error("Interview ID was not found.")
        if st.button("Return to Interview Setup"):
            go_to("setup")
        return

    try:
        interview_data = load_interview(interview_id)
    except Exception:
        interview_data = None

    if not interview_data:
        st.error("Unable to load this interview. Please return to setup and try again.")
        if st.button("Return to Interview Setup", key="load_error_setup"):
            go_to("setup")
        return

    interview = interview_data["interview"]
    questions = interview_data["questions"]
    if not questions:
        st.error("No interview questions were found. Please create a new interview.")
        if st.button("Create New Interview", key="no_questions_setup"):
            go_to("setup")
        return

    total_questions = len(questions)
    current_index = max(0, min(st.session_state.current_question, total_questions - 1))
    st.session_state.current_question = current_index
    current_question = questions[current_index]
    question_id = current_question["id"]
    question_text = current_question["question_text"]
    current_number = current_index + 1
    progress_percentage = int((current_number / total_questions) * 100)

    sidebar_column, content_column = st.columns([0.19, 0.81], gap="large")
    with sidebar_column:
        show_sidebar()

    with content_column:
        header_left, header_right = st.columns([0.78, 0.22])
        with header_left:
            html_block("interview-title", f"{interview.get('role', 'AI')} Interview")
            html_block("interview-meta", f"{interview.get('interview_type', 'Interview')} • {interview.get('difficulty', 'Medium')} • {total_questions} Questions")

        with header_right:
            if st.button("End Interview", key="end_interview_button", type="secondary"):
                try:
                    with st.spinner("Preparing your interview report..."):
                        final_result = finalize_interview(interview_id)
                    if final_result:
                        st.session_state.final_result = final_result
                        go_to("results")
                    else:
                        st.error("The interview report could not be prepared. Please try again.")
                except Exception:
                    st.error("The interview could not be finalized right now. Please try again.")

        details_column, question_column = st.columns([0.28, 0.72], gap="large")
        with details_column:
            candidate_name = interview.get("candidate_name", st.session_state.candidate_name)
            role = interview.get("role", st.session_state.role)
            skills = interview.get("skills", "Not specified")
            experience = interview.get("experience", "Not specified")
            interview_type = interview.get("interview_type", "Not specified")
            difficulty = interview.get("difficulty", "Not specified")

            st.markdown(
                f"""
                <div class="candidate-card">
                    <div class="candidate-card-title">Candidate Details</div>
                    <div class="candidate-label">Candidate</div><div class="candidate-value">{candidate_name}</div>
                    <div class="candidate-label">Job Role</div><div class="candidate-value">{role}</div>
                    <div class="candidate-label">Skills</div><div class="candidate-value">{skills}</div>
                    <div class="candidate-label">Experience</div><div class="candidate-value">{experience}</div>
                    <div class="candidate-label">Interview Type</div><div class="candidate-value">{interview_type}</div>
                    <div class="candidate-label">Difficulty</div><div class="candidate-value">{difficulty}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            html_block("interview-tip", "💡 <b>Interview Tip</b><br><br>Answer naturally and explain your thought process clearly. Your response will be evaluated by AI using a hidden question-specific rubric.")

        with question_column:
            st.markdown(
                f"""
                <div class="question-progress-top">
                    <div class="question-counter">Question {current_number} of {total_questions}</div>
                    <div class="question-percentage">{progress_percentage}%</div>
                </div>
                <div class="question-progress-track">
                    <div class="question-progress-fill" style="width:{progress_percentage}%;"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            safe_question = str(question_text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(
                f"""
                <div class="question-card">
                    <div class="question-number">QUESTION {current_number:02d}</div>
                    <div class="question-text">{safe_question}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            html_block("answer-heading", "Your Answer")
            html_block("answer-help", "Write a clear and complete answer. Explain your reasoning where relevant.")
            answer_key = f"answer_question_{question_id}"
            if answer_key not in st.session_state:
                st.session_state[answer_key] = st.session_state.answers.get(question_id, "")

            candidate_answer = st.text_area("Answer", key=answer_key, placeholder="Type your answer here...", label_visibility="collapsed", height=190)
            previous_column, spacer, submit_column = st.columns([0.27, 0.38, 0.35])

            with previous_column:
                if current_index > 0 and st.button("← Previous", key=f"previous_{question_id}", type="secondary"):
                    st.session_state.answers[question_id] = candidate_answer
                    st.session_state.current_question -= 1
                    st.rerun()

            with submit_column:
                is_last_question = current_index == total_questions - 1
                button_text = "Finish Interview →" if is_last_question else "Submit Answer →"
                if st.button(button_text, key=f"submit_{question_id}"):
                    if not candidate_answer.strip():
                        st.warning("Please enter an answer before submitting.")
                    else:
                        st.session_state.answers[question_id] = candidate_answer
                        if question_id in st.session_state.evaluations:
                            evaluation_result = {"success": True, "evaluation": st.session_state.evaluations[question_id]}
                        else:
                            try:
                                with st.spinner("AI is evaluating your answer..."):
                                    evaluation_result = evaluate_answer(
                                        interview_id=interview_id,
                                        question_id=question_id,
                                        candidate_answer=candidate_answer,
                                    )
                            except Exception:
                                evaluation_result = {
                                    "success": False,
                                    "message": (
                                        "AI evaluation is temporarily unavailable. "
                                        "Your answer is still here—please try submitting it again."
                                    ),
                                }

                        if not evaluation_result.get("success"):
                            st.error(evaluation_result.get("message", "Answer evaluation failed."))
                        else:
                            st.session_state.evaluations[question_id] = evaluation_result["evaluation"]
                            if not is_last_question:
                                st.session_state.current_question += 1
                                st.rerun()
                            else:
                                try:
                                    with st.spinner("Preparing your final interview report..."):
                                        final_result = finalize_interview(interview_id)
                                    if final_result:
                                        st.session_state.final_result = final_result
                                        go_to("results")
                                    else:
                                        st.error("Your answer was saved, but the final report could not be prepared. Please try again.")
                                except Exception:
                                    st.error("Your answer was saved, but the final report is temporarily unavailable. Please try again.")


# ============================================================
# FINAL RESULTS PAGE

# ============================================================
# INTERVIEW HISTORY PAGE
# ============================================================

def show_history():
    import html
    from datetime import datetime

    st.markdown('<div class="history-page-marker"></div>', unsafe_allow_html=True)
    st.markdown(HISTORY_CSS, unsafe_allow_html=True)

    try:
        history = get_interview_history()
    except Exception:
        st.error("Unable to load interview history right now. Please try again.")
        history = []

    sidebar_col, main_col = st.columns([0.19, 0.81], gap="large")

    with sidebar_col:
        show_sidebar()

    with main_col:
        html_block("history-title", "Interview History")
        html_block(
            "history-subtitle",
            "Review previous AI interviews and reopen completed reports.",
        )

        completed_count = sum(
            1 for item in history
            if str(item.get("status", "")).upper() == "COMPLETED"
        )

        st.markdown(
            f"""
            <div class="history-summary-card">
                <div class="history-summary-small">Your Interview Journey</div>
                <div class="history-summary-value">
                    {completed_count} Completed Interview{"s" if completed_count != 1 else ""}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not history:
            st.markdown(
                """
                <div class="history-empty">
                    <div class="history-empty-icon">🗂️</div>
                    <div class="history-empty-title">No interviews yet</div>
                    Start your first AI interview and it will appear here.
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("＋ Start Your First Interview", key="history_first"):
                go_to("setup")
            return

        for item in history:
            interview_id = item.get("id")
            role = item.get("role") or "Interview"
            status = str(item.get("status") or "").upper()

            st.markdown(
                f"""
<div style="background:#ffffff;border:1px solid #dce8f5;border-radius:18px;
padding:20px 24px;margin:0 0 8px 0;box-shadow:0 8px 24px rgba(31,75,125,.06);">
  <div style="color:#0b173d;font-size:21px;font-weight:800;">{html.escape(str(role))}</div>
</div>
                """.strip(),
                unsafe_allow_html=True,
            )

            if status == "COMPLETED":
                if st.button(
                    "View Report  →",
                    key=f"history_view_{interview_id}",
                    use_container_width=True,
                ):
                    try:
                        st.session_state.interview_id = interview_id
                        final_result = finalize_interview(interview_id)
                        if final_result:
                            st.session_state.final_result = final_result
                            go_to("results")
                        else:
                            st.error("Unable to open this report right now. Please try again.")
                    except Exception:
                        st.error("Unable to open this report right now. Please try again.")
            else:
                st.caption("Report will be available after the interview is completed.")

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


def build_interview_pdf(final_data):
    """Builds a professional PDF report in memory and returns PDF bytes."""
    from io import BytesIO
    from xml.sax.saxutils import escape

    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, KeepTogether
        )
    except ImportError as exc:
        raise RuntimeError(
            "PDF support requires ReportLab. Run: pip install reportlab"
        ) from exc

    interview = final_data.get("interview") or {}
    questions = final_data.get("questions") or []
    result = final_data.get("result") or {}
    performance = final_data.get("performance", "Completed")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="AI Interview Generator - Interview Report",
        author="AI Interview Generator",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=22, leading=27, textColor=colors.HexColor("#0B173D"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"], fontSize=10.5, leading=15,
        textColor=colors.HexColor("#66758F"), spaceAfter=14
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=14, leading=18, textColor=colors.HexColor("#0B173D"),
        spaceBefore=10, spaceAfter=8
    )
    question_style = ParagraphStyle(
        "Question", parent=styles["Heading3"], fontName="Helvetica-Bold",
        fontSize=11.5, leading=16, textColor=colors.HexColor("#0B173D"),
        spaceAfter=7
    )
    label_style = ParagraphStyle(
        "Label", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=8.5, leading=12, textColor=colors.HexColor("#405474"),
        spaceBefore=5, spaceAfter=2
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["BodyText"], fontSize=9.5, leading=14,
        textColor=colors.HexColor("#263454"), spaceAfter=5
    )
    score_style = ParagraphStyle(
        "Score", parent=styles["Normal"], alignment=TA_CENTER,
        fontName="Helvetica-Bold", fontSize=18, leading=22,
        textColor=colors.HexColor("#1268ED")
    )

    def clean(value, default="-"):
        if value in (None, "", []):
            return default
        if isinstance(value, list):
            return "<br/>".join("- " + escape(str(x)) for x in value) or default
        if isinstance(value, dict):
            return "<br/>".join(
                f"<b>{escape(str(k))}:</b> {escape(str(v))}" for k, v in value.items()
            ) or default
        return escape(str(value)).replace("\n", "<br/>")

    def first_value(data, names, default=""):
        if not isinstance(data, dict):
            return default
        for name in names:
            value = data.get(name)
            if value not in (None, "", []):
                return value
        return default

    story = []
    story.append(Paragraph("AI Interview Generator", title_style))
    story.append(Paragraph("Personalized AI Interview Report", subtitle_style))

    details = [
        ["Candidate", clean(interview.get("candidate_name")), "Job Role", clean(interview.get("role"))],
        ["Skills", clean(interview.get("skills")), "Experience", clean(interview.get("experience"))],
        ["Interview Type", clean(interview.get("interview_type")), "Difficulty", clean(interview.get("difficulty"))],
        ["Date", clean(interview.get("created_at")), "Status", clean(interview.get("status", "COMPLETED"))],
    ]
    detail_table = Table(details, colWidths=[28*mm, 60*mm, 28*mm, 60*mm])
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F5F9FE")),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#263454")),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#DCE8F5")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    story.append(detail_table)
    story.append(Spacer(1, 10))

    total_score = result.get("total_score", result.get("score", 0))
    max_score = result.get("maximum_score", result.get("max_score", 0))
    percentage = result.get("percentage", 0)
    summary = Table([
        [Paragraph(clean(total_score) + " / " + clean(max_score), score_style),
         Paragraph(clean(percentage) + "%", score_style),
         Paragraph(clean(performance), score_style)],
        ["TOTAL SCORE", "PERCENTAGE", "PERFORMANCE"]
    ], colWidths=[58*mm, 58*mm, 58*mm])
    summary.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#EDF6FF")),
        ("BOX", (0,0), (-1,-1), 0.8, colors.HexColor("#CFE3F8")),
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#DCE8F5")),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,1), (-1,1), "Helvetica-Bold"),
        ("FONTSIZE", (0,1), (-1,1), 8),
        ("TEXTCOLOR", (0,1), (-1,1), colors.HexColor("#66758F")),
        ("TOPPADDING", (0,0), (-1,0), 10),
        ("BOTTOMPADDING", (0,0), (-1,0), 7),
        ("TOPPADDING", (0,1), (-1,1), 5),
        ("BOTTOMPADDING", (0,1), (-1,1), 8),
    ]))
    story.append(summary)
    story.append(Spacer(1, 12))
    story.append(Paragraph("Question-wise Analysis", section_style))

    for index, question in enumerate(questions, start=1):
        evaluation = question.get("evaluation") or {}
        answer = first_value(question, ["candidate_answer", "answer"], "-")
        q_score = first_value(evaluation, ["score", "total_score", "marks", "points"], first_value(question, ["score", "marks"], "-"))
        q_max = first_value(evaluation, ["max_score", "maximum_score", "max_marks", "total_marks"], first_value(question, ["max_score"], ""))
        strengths = first_value(evaluation, ["strengths", "strength", "what_was_good", "positive_points"], "-")
        missing = first_value(evaluation, ["missing_concepts", "missing_points", "weaknesses", "areas_for_improvement", "improvements"], "-")
        feedback = first_value(evaluation, ["feedback", "ai_feedback", "detailed_feedback", "comments"], "-")
        ideal = first_value(evaluation, ["ideal_answer", "model_answer", "expected_answer", "suggested_answer"], "-")
        score_text = f"{q_score}/{q_max}" if q_max not in (None, "") else str(q_score)

        block = [
            Paragraph(f"QUESTION {index:02d}", label_style),
            Paragraph(clean(question.get("question_text", "Question")), question_style),
            Paragraph(f"<b>Score:</b> {clean(score_text)}", body_style),
            Paragraph("YOUR ANSWER", label_style),
            Paragraph(clean(answer), body_style),
            Paragraph("STRENGTHS", label_style),
            Paragraph(clean(strengths), body_style),
            Paragraph("MISSING CONCEPTS / IMPROVEMENTS", label_style),
            Paragraph(clean(missing), body_style),
            Paragraph("AI FEEDBACK", label_style),
            Paragraph(clean(feedback), body_style),
            Paragraph("IDEAL ANSWER", label_style),
            Paragraph(clean(ideal), body_style),
            Spacer(1, 9),
        ]
        story.append(KeepTogether(block[:3]))
        story.extend(block[3:])

        if index < len(questions):
            story.append(Spacer(1, 4))

    def add_page_number(canvas, doc_obj):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#7B899F"))
        canvas.drawRightString(A4[0] - 16*mm, 9*mm, f"Page {doc_obj.page}")
        canvas.drawString(16*mm, 9*mm, "AI Interview Generator")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def show_results():
    import html

    st.markdown('<div class="results-page-marker"></div>', unsafe_allow_html=True)
    st.markdown(RESULTS_CSS, unsafe_allow_html=True)

    final_data = st.session_state.final_result
    interview_id = st.session_state.interview_id

    if not final_data and interview_id:
        try:
            final_data = finalize_interview(interview_id)
            st.session_state.final_result = final_data
        except Exception:
            st.error("Unable to load the final result right now. Please try again.")
            if st.button("← Back to Interview Setup"):
                go_to("setup")
            return

    if not final_data:
        st.error("No completed interview result was found.")
        if st.button("← Back to Interview Setup"):
            go_to("setup")
        return

    interview = final_data.get("interview") or {}
    questions = final_data.get("questions") or []
    result = final_data.get("result") or {}
    performance = final_data.get("performance", "Completed")

    percentage = result.get("percentage", 0)
    try:
        percentage_display = f"{float(percentage):.0f}%"
    except (TypeError, ValueError):
        percentage_display = str(percentage)

    total_score = result.get("total_score", result.get("score", "—"))
    max_score = result.get("max_score", result.get("maximum_score", ""))
    score_display = f"{total_score}/{max_score}" if max_score not in (None, "") else str(total_score)

    sidebar_col, main_col = st.columns([0.19, 0.81], gap="large")
    with sidebar_col:
        show_sidebar()

    with main_col:
        html_block("results-title", "Interview Completed 🎉")
        name = html.escape(str(interview.get("candidate_name", st.session_state.candidate_name)))
        role = html.escape(str(interview.get("role", st.session_state.role)))
        html_block("results-subtitle", f"{name} • {role}")
        st.markdown(f'<div class="results-hero"><div class="results-hero-small">Overall Interview Result</div><div class="results-score">{html.escape(percentage_display)}</div><div class="results-performance">{html.escape(str(performance))}</div></div>', unsafe_allow_html=True)

        c1,c2,c3=st.columns(3,gap="medium")
        with c1: st.markdown(f'<div class="results-card"><div class="results-card-label">Total Score</div><div class="results-card-value">{html.escape(score_display)}</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="results-card"><div class="results-card-label">Percentage</div><div class="results-card-value">{html.escape(percentage_display)}</div></div>',unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="results-card"><div class="results-card-label">Performance</div><div class="results-card-value">{html.escape(str(performance))}</div></div>',unsafe_allow_html=True)

        html_block("results-section-title", "Question-wise Analysis")

        def first_value(data,names,default=""):
            if not isinstance(data,dict): return default
            for n in names:
                v=data.get(n)
                if v not in (None,"",[]): return v
            return default

        def show_value(v):
            if isinstance(v,list): return "• " + "\n• ".join(str(x) for x in v) if v else "—"
            if isinstance(v,dict): return "\n".join(f"{k}: {val}" for k,val in v.items())
            return str(v) if v not in (None,"") else "—"

        for index,q in enumerate(questions,start=1):
            qid=q.get("id")
            ev=st.session_state.evaluations.get(qid) or q.get("evaluation") or {}
            answer=first_value(q,["candidate_answer","answer"],st.session_state.answers.get(qid,"—"))
            score=first_value(ev,["score","total_score","marks","points"],first_value(q,["score","marks"],"—"))
            maxq=first_value(ev,["max_score","maximum_score","max_marks","total_marks"],"")
            qscore=f"{score}/{maxq}" if maxq not in (None,"") else str(score)
            strengths=first_value(ev,["strengths","strength","what_was_good","positive_points"],"—")
            missing=first_value(ev,["missing_concepts","missing_points","weaknesses","areas_for_improvement","improvements"],"—")
            feedback=first_value(ev,["feedback","ai_feedback","detailed_feedback","comments"],"—")
            ideal=first_value(ev,["ideal_answer","model_answer","expected_answer","suggested_answer"],"—")
            qtext=html.escape(str(q.get("question_text","Question")))
            st.markdown(f'<div class="result-question-card"><div class="result-q-number">QUESTION {index:02d}</div><div class="result-q-text">{qtext}</div><div class="result-chip">Score: {html.escape(qscore)}</div><div class="result-block"><div class="result-block-title">Your Answer</div><div class="result-block-text">{html.escape(show_value(answer))}</div></div><div class="result-block"><div class="result-block-title">Strengths</div><div class="result-block-text">{html.escape(show_value(strengths))}</div></div><div class="result-block"><div class="result-block-title">Missing Concepts / Improvements</div><div class="result-block-text">{html.escape(show_value(missing))}</div></div><div class="result-block"><div class="result-block-title">AI Feedback</div><div class="result-block-text">{html.escape(show_value(feedback))}</div></div><div class="result-block"><div class="result-block-title">Ideal Answer</div><div class="result-block-text">{html.escape(show_value(ideal))}</div></div></div>',unsafe_allow_html=True)

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

        try:
            pdf_bytes = build_interview_pdf(final_data)
            safe_name = str(interview.get("candidate_name", "candidate")).strip().replace(" ", "_")
            safe_role = str(interview.get("role", "interview")).strip().replace(" ", "_")
            st.download_button(
                label="⬇ Download Interview Report (PDF)",
                data=pdf_bytes,
                file_name=f"AI_Interview_Report_{safe_name}_{safe_role}.pdf",
                mime="application/pdf",
                key="download_interview_pdf",
                use_container_width=True,
            )
        except Exception:
            st.warning("PDF report is temporarily unavailable. The interview result is still saved.")

        left,right=st.columns(2,gap="medium")
        with left:
            if st.button("＋ Start New Interview",key="results_new_main"):
                st.session_state.current_question=0; st.session_state.answers={}; st.session_state.evaluations={}; st.session_state.final_result=None; st.session_state.interview_id=None; st.session_state.interview_data=None
                go_to("setup")
        with right:
            if st.button("⌂ Back to Home",key="results_home_main",type="secondary"):
                go_to("welcome")





SIDEBAR_HISTORY_BLUE_CSS = """
<style>
/* Keep the original Interview History navigation blue, matching New Interview/About */
div[data-testid="stElementContainer"]:has(.sidebar-history-button-marker) + div button,
div[data-testid="stElementContainer"]:has(.sidebar-history-button-marker) + div button:hover,
div[data-testid="stElementContainer"]:has(.sidebar-history-button-marker) + div button:focus,
div[data-testid="stElementContainer"]:has(.sidebar-history-button-marker) + div button:active {
    width: 100% !important;
    min-height: 52px !important;
    background: linear-gradient(135deg,#1677ff 0%,#318cff 100%) !important;
    background-color: #1677ff !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    opacity: 1 !important;
    box-shadow: 0 8px 18px rgba(22,119,255,.18) !important;
    font-weight: 700 !important;
}
div[data-testid="stElementContainer"]:has(.sidebar-history-button-marker) + div button p,
div[data-testid="stElementContainer"]:has(.sidebar-history-button-marker) + div button * {
    color: #ffffff !important;
    opacity: 1 !important;
}
</style>
"""

ABOUT_CSS = """
<style>
/* About page layout */
.stApp:has(.about-page-marker) [data-testid="stMainBlockContainer"],
.stApp:has(.about-page-marker) .block-container {
    max-width: 100% !important;
    padding: .6rem 3.5rem 2rem !important;
}

/* Same dark sidebar treatment used by Results/History */
.stApp:has(.about-page-marker)
:is(div[data-testid="column"], div[data-testid="stColumn"]):has(.sidebar-brand) {
    background:
        radial-gradient(circle at 50% 72%, rgba(40,127,255,.30), transparent 58%),
        linear-gradient(180deg,#0b1838 0%,#040a18 100%) !important;
    border-radius: 18px !important;
    padding: 26px 18px 22px !important;
    box-shadow: 0 16px 36px rgba(4,10,24,.35) !important;
    position: sticky !important;
    top: 10px !important;
    align-self: flex-start !important;
    height: calc(100vh - 20px) !important;
    max-height: calc(100vh - 20px) !important;
    overflow: hidden !important;
    z-index: 50 !important;
}

.stApp:has(.about-page-marker) .sidebar-brand {
    color: #ffffff !important;
    font-size: 25px !important;
}
.stApp:has(.about-page-marker) .sidebar-blue { color:#4da3ff !important; }
.stApp:has(.about-page-marker) .sidebar-quote { color:#b9c7e2 !important; }
.stApp:has(.about-page-marker) .sidebar-divider {
    background: rgba(255,255,255,.22) !important;
}

/* Keep original sidebar buttons readable on About */
.stApp:has(.about-page-marker)
div[data-testid="stElementContainer"]:has(.sidebar-new-interview-button-marker) + div button {
    color:#ffffff !important;
}
.stApp:has(.about-page-marker)
div[data-testid="stElementContainer"]:has(.sidebar-about-button-marker) + div button {
    color:#ffffff !important;
}
.stApp:has(.about-page-marker)
div[data-testid="stElementContainer"]:has(.sidebar-about-button-marker) + div button {
    background:rgba(39,126,255,.16) !important;
    color:#ffffff !important;
}

/* Main About content */
.about-hero {
    background: linear-gradient(135deg,#0d6efd 0%,#49a4ff 100%) !important;
    border-radius: 22px !important;
    padding: 32px 34px !important;
    box-shadow: 0 14px 34px rgba(25,112,235,.20) !important;
    margin-bottom: 20px !important;
}
.about-hero h1 {
    margin:0 0 8px !important;
    font-size:36px !important;
    font-weight:800 !important;
    color:#ffffff !important;
}
.about-hero p {
    margin:0 !important;
    color:#ffffff !important;
    font-size:15px !important;
    line-height:1.65 !important;
    opacity:.96 !important;
}

.about-section {
    background:#ffffff !important;
    border:1px solid #dce8f5 !important;
    border-radius:17px !important;
    padding:22px 24px !important;
    margin:16px 0 !important;
    box-shadow:0 8px 24px rgba(31,75,125,.07) !important;
}
.about-section h3 {
    margin:0 0 10px !important;
    color:#0b173d !important;
    font-size:21px !important;
    font-weight:800 !important;
}
.about-section p {
    margin:0 !important;
    color:#526582 !important;
    line-height:1.7 !important;
    font-size:14px !important;
}

.about-grid {
    display:grid !important;
    grid-template-columns:repeat(2,minmax(0,1fr)) !important;
    gap:15px !important;
    margin:16px 0 !important;
}
.about-card {
    display:block !important;
    background:#f7faff !important;
    border:1px solid #dce8f5 !important;
    border-radius:16px !important;
    padding:20px 21px !important;
}
.about-card h4 {
    margin:0 0 8px !important;
    color:#15315d !important;
    font-size:16px !important;
    font-weight:800 !important;
}
.about-card p {
    margin:0 !important;
    color:#61718a !important;
    line-height:1.6 !important;
    font-size:13px !important;
}

.about-flow {
    display:flex !important;
    align-items:stretch !important;
    gap:10px !important;
    flex-wrap:wrap !important;
    margin-top:16px !important;
}
.about-step {
    flex:1 1 135px !important;
    background:#f3f8ff !important;
    border:1px solid #d9e8fa !important;
    border-radius:13px !important;
    padding:13px 10px !important;
    text-align:center !important;
    font-weight:800 !important;
    color:#23436f !important;
}

.about-tech {
    display:flex !important;
    flex-wrap:wrap !important;
    gap:9px !important;
    margin-top:14px !important;
}
.about-pill {
    display:inline-block !important;
    background:#edf5ff !important;
    color:#1769d2 !important;
    border:1px solid #d7e9ff !important;
    border-radius:999px !important;
    padding:8px 13px !important;
    font-weight:800 !important;
    font-size:13px !important;
}
.about-footer {
    text-align:center !important;
    color:#8190a7 !important;
    padding:18px 0 4px !important;
    font-size:13px !important;
}

@media (max-width:900px) {
    .about-grid { grid-template-columns:1fr !important; }
}
</style>
"""

def show_about():
    # Use the same explicit sidebar/main-column structure as the rest of the application.
    sidebar_col, main_col = st.columns([1.45, 6.55], gap="large")

    with sidebar_col:
        show_sidebar()

    with main_col:
        st.markdown('<div class="about-page-marker"></div>', unsafe_allow_html=True)
        st.markdown(ABOUT_CSS, unsafe_allow_html=True)

        st.markdown("""
<div class="about-hero">
    <h1>AI Interview Generator</h1>
    <p>Practice Smarter with AI. A role-focused interview preparation platform that generates relevant questions, evaluates candidate responses, and turns every interview into actionable feedback.</p>
</div>

<div class="about-section">
    <h3>About the Platform</h3>
    <p>AI Interview Generator makes interview practice structured and personalized. Candidates select their target role, skills, experience level, difficulty, and interview type. The system creates an AI-powered interview, evaluates submitted answers, and provides a detailed performance report.</p>
</div>

<div class="about-grid">
    <div class="about-card">
        <h4>✦ AI Generated Questions</h4>
        <p>Creates role-specific questions using the selected skills, experience, difficulty, and interview type.</p>
    </div>
    <div class="about-card">
        <h4>✓ Detailed Evaluation</h4>
        <p>Evaluates every submitted response against an AI-generated rubric and provides a question-wise score.</p>
    </div>
    <div class="about-card">
        <h4>◎ Personalized Feedback</h4>
        <p>Shows strengths, missing concepts, areas for improvement, AI feedback, and an ideal answer for every question.</p>
    </div>
    <div class="about-card">
        <h4>◷ Interview History & Reports</h4>
        <p>Stores completed interviews, lets candidates revisit previous results, and provides downloadable PDF reports.</p>
    </div>
</div>

<div class="about-section">
    <h3>How It Works</h3>
    <div class="about-flow">
        <div class="about-step">1. Setup</div>
        <div class="about-step">2. AI Questions</div>
        <div class="about-step">3. Interview</div>
        <div class="about-step">4. AI Evaluation</div>
        <div class="about-step">5. Results</div>
    </div>
</div>

<div class="about-section">
    <h3>Technology Stack</h3>
    <p>The platform combines a Python interface, generative AI, persistent local storage, and PDF report generation.</p>
    <div class="about-tech">
        <span class="about-pill">Python</span>
        <span class="about-pill">Streamlit</span>
        <span class="about-pill">Gemini AI</span>
        <span class="about-pill">SQLite</span>
        <span class="about-pill">ReportLab</span>
    </div>
</div>

<div class="about-section">
    <h3>Project Purpose</h3>
    <p>The goal is to provide a complete AI-assisted interview practice environment where candidates can repeatedly practice, receive immediate structured evaluation, identify knowledge gaps, and track previous interview performance from one application.</p>
</div>

<div class="about-footer">AI Interview Generator • Version 1.0 • Practice Smarter with AI</div>
        """, unsafe_allow_html=True)


# ============================================================
# ROUTER
# ============================================================

def main():
    page = st.session_state.page

    if page == "welcome":
        show_welcome()
    elif page == "setup":
        show_setup()
    elif page == "generated":
        show_generated()
    elif page == "interview":
        show_interview()
    elif page == "results":
        show_results()
    elif page == "history":
        show_history()
    elif page == "about":
        show_about()
    else:
        st.session_state.page = "welcome"
        st.rerun()


# ============================================================

# RUN APPLICATION

# ============================================================



if __name__ == "__main__":

    main()