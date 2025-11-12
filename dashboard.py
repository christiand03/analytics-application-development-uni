import streamlit as st
from streamlit_option_menu import option_menu
from app_pages import page1, page2, page3, page4

st.set_page_config(page_icon="🛡️", layout="wide")

st.title("Data Quality Dashboard")

# --- NAVIGATION ---
# Die Magie passiert hier!
selected = option_menu(
    menu_title=None,  # Erforderlich, aber kann auf None gesetzt werden
    options=["Page 1", "Page 2", "Page 3", "Page 4"],  # Namen der Seiten
    icons=["house", "shield-check", "search", "graph-up-arrow"],  # Optionale Bootstrap Icons
    menu_icon="cast",  # Optional
    default_index=0,  # Seite, die standardmäßig angezeigt wird
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "25px"},
        "nav-link": {
            "font-size": "18px",
            "color": "#000000",
            "text-align": "left",
            "margin": "0px",
            "--hover-color": "#eee",
        },
        "nav-link-selected": {
            "background-color": "#02ab21",
            "color": "white"
            },
        
    },
)

# --- SEITEN-ROUTING ---
# Basierend auf der Auswahl in der Navigation wird die entsprechende Seite geladen
if selected == "Page 1":
    page1.show_page()
elif selected == "Page 2":
    page2.show_page()
elif selected == "Page 3":
    page3.show_page()
elif selected == "Page 4":
    page4.show_page()
