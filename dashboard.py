import time
import pandas as pd
import streamlit as st
import metrics as mt
from streamlit_option_menu import option_menu
from app_pages import page1, page2, page3, page4, page5

# --- Data Loading ---
start_time = time.time()
@st.cache_data
def load():
    df = pd.read_parquet("resources/Auftragsdaten_konvertiert")
    df2 = pd.read_parquet("resources/Positionsdaten_konvertiert")
    return df, df2

df, df2 = load()
load_time = time.time()
loading_time = load_time - start_time
print(f"Loaded Data in "+str(round(loading_time,2))+"s")



# --- METRIKEN BERECHNEN ---

# Metriken für den ersten DataFrame (df - Auftragsdaten)
print("Calculating metrics for df1 (Auftragsdaten)...")
calc_time_t1 = time.time()
#plausi_diff_list, plausi_count, plausi_avg = mt.plausibilitaetscheck_forderung_einigung(df)
calc_time_t2 = time.time()
print("Calculated plausi_diff_list, plausi_count, plausi_avg in"+str(round(calc_time_t2-calc_time_t1,2))+"s") 
#zeitwert_errors_list = mt.check_zeitwert(df)
calc_time_t1 = time.time()
print("Calculated zeitwert_errors_list in"+str(round(calc_time_t1-calc_time_t2,2))+"s") 
proforma_df, proforma_count = mt.proformabelege(df)
calc_time_t2 = time.time()
print("Calculated proforma_df, proforma_count in"+str(round(calc_time_t2-calc_time_t1,2))+"s") 
grouped_col_ratios_df1, grouped_row_ratios_df1 = mt.data_cleanliness(df)
calc_time_t1 = time.time()
print("Calculated grouped_col_ratios_df1, grouped_row_ratios_df1 in"+str(round(calc_time_t1-calc_time_t2,2))+"s") 
error_freq_df = mt.error_frequency_by_weekday_hour(
                                                    df,
                                                    time_col="CRMEingangszeit",
                                                    relevant_columns=None
                                                )
calc_time_t2 = time.time()
print("Calculated error_freq_df (by weekday) in"+str(round(calc_time_t2-calc_time_t1,2))+"s") 

metrics_df1 = {
    "row_count": mt.count_rows(df),
    "null_ratio_cols": mt.ratio_null_values_column(df),
    "null_ratio_rows": mt.ratio_null_values_rows(df),
    "test_kundengruppen_anzahl": mt.Kundengruppe_containing_test(df),
    "statistiken_num": mt.allgemeine_statistiken_num(df),
    #"plausi_forderung_einigung_list": plausi_diff_list,
    #"plausi_forderung_einigung_count": plausi_count,
    #"plausi_forderung_einigung_avg_diff": plausi_avg,
    "grouped_col_ratios": grouped_col_ratios_df1,
    "grouped_row_ratios": grouped_row_ratios_df1,
    "proforma_belege_df": proforma_df,
    "proforma_belege_count": proforma_count,
    "above_50k_df": mt.above_50k(df),
    #"zeitwert_errors_list": zeitwert_errors_list,
    #"zeitwert_errors_count": len(zeitwert_errors_list),
    "error_frequency_weekday_hour": error_freq_df,
}
#    "einigung_negativ_count": mt.einigung_negativ(df), fehlt

# Metriken für den zweiten DataFrame (df2 - Positionsdaten)
print("Calculating metrics for df2 (Positionsdaten)...")
metrics_df2 = {
    "row_count": mt.count_rows(df2),
    "null_ratio_cols": mt.ratio_null_values_column(df2),
    "null_ratio_rows": mt.ratio_null_values_rows(df2),
    "statistiken_num": mt.allgemeine_statistiken_num(df2),
    "discount_check_errors": mt.discount_check(df2),
    "position_counts_per_rechnung": mt.position_count(df2)
}

# Metriken, die beide DataFrames benötigen
print("Calculating combined metrics...")
kva_id_unique, pos_id_unique = mt.uniqueness_check(df, df2)
metrics_combined = {
    "kvarechnung_id_is_unique": kva_id_unique,
    "position_id_is_unique": pos_id_unique
}
print("Calculating positions per order over time...")
positions_over_time_df = mt.positions_per_order_over_time(
    df,
    df2,
    time_col="CRMEingangszeit"
)
print("All metrics calculated.")

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
            "nav-link": {
                "font-size": "14px",
                "color": "#c1c1c1",
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
            "nav-link-selected": {
                "background-color": "#442D7B",
                "color": "#c1c1c1",
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
    page1.show_page(df, df2, metrics_df1, metrics_df2, metrics_combined)
elif selected == "Numerische Daten":
    page2.show_page(df, df2, metrics_df1, metrics_df2, metrics_combined)
elif selected == "Textuelle Daten":
    page3.show_page(df, df2, metrics_df1, metrics_df2, metrics_combined)
elif selected == "Plausibilitätscheck":
    page4.show_page(df, df2, metrics_df1, metrics_df2, metrics_combined)
elif selected == "Detailansicht":
    page5.show_page(df, df2, metrics_df1, metrics_df2, metrics_combined)