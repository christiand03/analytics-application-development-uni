import streamlit as st
from streamlit_option_menu import option_menu
from app_pages import page1, page2, page3, page4, page5

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Data Quality Dashboard",
    page_icon="assets/logo.png",
    layout="wide"
)

# --- CSS-INJEKTION FÜR KOMPAKTES LAYOUT & STYLING ---
st.markdown("""
    <style>
        div.block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        header {
            visibility: hidden;
        }
    </style>
""", unsafe_allow_html=True)


# --- HEADER ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/logo.png")


# --- NAVIGATION ---
selected = option_menu(
    menu_title=None,
    options=["Startseite","Numerische Daten", "Textuelle Daten", "Plausibilitätscheck", "Detailansicht"],
    icons=["house", "graph-up-arrow", "bar-chart-steps", "pie-chart", "clipboard2-data"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "5px!important",
            "background-color": "transparent",
        },
        "icon": {
            "color": "#c1c1c1",
            "font-size": "20px"
        },
        # Style für die inaktiven/nicht ausgewählten Buttons
        "nav-link": {
            "font-size": "15px",
            "color": "#888",
            "background-color": "transparent",
            "border": "1px solid #222",
            "border-radius": "4px",  # <-- GEÄNDERT: Nur sehr leicht abgerundet
            "margin": "0px 5px",
            "padding": "8px 20px",
            "flex-grow": "1",
            "display": "flex",
            "justify-content": "center",
            "align-items": "center",
            "gap": "10px",
            "--hover-color": "#2a2a2f",
        },
        # Style für den aktiven/ausgewählten Button
        "nav-link-selected": {
            "background-color": "#007bff",
            "color": "white",
            "font-weight": "bold",
            "font-size": "15px",
            "padding": "8px 20px",
            "border": "1px solid #007bff",
            "border-radius": "4px",  # <-- GEÄNDERT: Nur sehr leicht abgerundet
            "box-shadow": "0 2px 5px rgba(0,0,0,0.2)", # <-- HINZUGEFÜGT: Schatteneffekt
            "display": "flex",
            "justify-content": "center",
            "align-items": "center",
            "gap": "10px",
        },
    },
)

# --- SEITEN-ROUTING ---
if selected == "Startseite":
    page1.show_page()
elif selected == "Numerische Daten":
    page2.show_page()
elif selected == "Textuelle Daten":
    page3.show_page()
elif selected == "Plausibilitätscheck":
    page4.show_page()
elif selected == "Detailansicht":
    page5.show_page()