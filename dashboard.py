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
nav_col1, nav_col2, nav_col3 = st.columns([1, 4, 1])
with nav_col2:
    selected = option_menu(
        menu_title=None,
        options=[
            "Startseite",
            "Numerische Daten",
            "Textuelle Daten",
            "Plausibilitätscheck",
            "Detailansicht"
        ],
        icons=[
            "house",
            "graph-up-arrow",
            "bar-chart-steps",
            "pie-chart",
            "clipboard2-data"
        ],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0.3rem",
                "background-color": "transparent",
                "border-radius": "999px",
                "border": "1px solid #e5e7eb",
            },
            "icon": {
                "font-size": "18px",
            },
            # Style für die inaktiven/nicht ausgewählten Buttons
            "nav-link": {
                "font-size": "14px",
                "color": "#888",
                "padding": "0.5rem 1.3rem",
                "margin": "0 0.1rem",
                "border-radius": "999px",
                "border": "none",
                "background-color": "transparent",
                "display": "flex",
                "justify-content": "center",
                "align-items": "center",
                "gap": "10px",
                "transition": "all 0.2s ease-in-out",
                "--hover-color": "#2a2a2f",
            },
            # Style für den aktiven/ausgewählten Button
            "nav-link-selected": {
                "background-color": "#442D7B",
                "color": "white",
                "font-weight": "bold",
                "font-size": "15px",
                "border-radius": "999px",
                "box-shadow": "0 4px 10px rgba(0,0,0,0.2)",
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