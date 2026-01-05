import time
import pandas as pd
import streamlit as st
import metrics as mt
from streamlit_option_menu import option_menu
from app_pages import page1, page2, page3, page4, page5

st.set_page_config(
    page_title="Data Quality Dashboard",
    page_icon="assets/logo.png",
    layout="wide"
)

@st.cache_data
def load():
    df = pd.read_parquet("resources/Auftragsdaten_konvertiert")
    df2 = pd.read_parquet("resources/Positionsdaten_konvertiert")
    return df, df2

@st.cache_data
def compute_metrics_df1():
    print("Calculating metrics for df1 (Auftragsdaten)...")
    df, _ = load()

    calc_time_start = time.time()
    plausi_diff_list, plausi_count, plausi_avg = mt.plausibilitaetscheck_forderung_einigung(df)
    print("Calculated plausi_diff_list, plausi_count, plausi_avg in "
          f"{round(time.time() - calc_time_start, 2)}s")

    calc_time_start = time.time()
    zeitwert_errors_series = mt.check_zeitwert(df)
    print("Calculated zeitwert_errors_list in "
          f"{round(time.time() - calc_time_start, 2)}s")

    calc_time_start = time.time()
    proforma_df, proforma_count = mt.proformabelege(df)
    print("Calculated proforma_df, proforma_count in "
          f"{round(time.time() - calc_time_start, 2)}s")

    calc_time_start = time.time()
    grouped_col_ratios_df1, grouped_row_ratios_df1 = mt.data_cleanliness(df)
    print("Calculated grouped_col_ratios_df1, grouped_row_ratios_df1 in "
          f"{round(time.time() - calc_time_start, 2)}s")

    calc_time_start = time.time()
    error_freq_df = mt.error_frequency_by_weekday_hour(
        df,
        time_col="CRMEingangszeit",
        relevant_columns=None
    )
    print("Calculated error_freq_df (by weekday) in "
          f"{round(time.time() - calc_time_start, 2)}s")

    calc_time_start = time.time()
    metrics_df1 = {
        "row_count": mt.count_rows(df),
        "null_ratio_cols": mt.ratio_null_values_column(df),
        "null_ratio_rows": mt.ratio_null_values_rows(df),
        "test_kundengruppen_anzahl": mt.Kundengruppe_containing_test(df),
        "statistiken_num": mt.allgemeine_statistiken_num(df),
        "plausi_forderung_einigung_list": plausi_diff_list,
        "plausi_forderung_einigung_count": plausi_count,
        "plausi_forderung_einigung_avg_diff": plausi_avg,
        "grouped_col_ratios": grouped_col_ratios_df1,
        "grouped_row_ratios": grouped_row_ratios_df1,
        "proforma_belege_df": proforma_df,
        "proforma_belege_count": proforma_count,
        "above_50k_df": mt.above_50k(df),
        "zeitwert_errors_list": zeitwert_errors_series,
        "zeitwert_errors_count": zeitwert_errors_series.size,
        "error_frequency_weekday_hour": error_freq_df,
        "false_negative": mt.false_negative_df(df)
    }
    print("Calculated all other metrics for df1 in "
          f"{round(time.time() - calc_time_start, 2)}s")

    return metrics_df1


@st.cache_data
def compute_metrics_df2():
    """Teure Metriken für df2 (Positionsdaten) – gecached."""
    print("Calculating metrics for df2 (Positionsdaten)...")
    _, df2 = load()
    calc_time_start = time.time()
    
    plausi_diff_list, plausi_count, plausi_avg = mt.plausibilitaetscheck_forderung_einigung(df2)
    print("Calculated plausi_diff_list, plausi_count, plausi_avg in "
          f"{round(time.time() - calc_time_start, 2)}s")
    
    metrics_df2 = {
        "row_count": mt.count_rows(df2),
        "null_ratio_cols": mt.ratio_null_values_column(df2),
        "null_ratio_rows": mt.ratio_null_values_rows(df2),
        "statistiken_num": mt.allgemeine_statistiken_num(df2),
        "discount_check_errors": mt.discount_check(df2),
        "position_counts_per_rechnung": mt.position_count(df2),
        "plausi_forderung_einigung_list": plausi_diff_list,
        "plausi_forderung_einigung_count": plausi_count,
        "plausi_forderung_einigung_avg_diff": plausi_avg,
        "false_negative": mt.false_negative_df2(df2)
    }
    print("Calculated all metrics for df2 in "
          f"{round(time.time() - calc_time_start, 2)}s")
    return metrics_df2


@st.cache_data
def compute_metrics_combined():
    """Metriken, die beide DataFrames brauchen – gecached."""
    print("Calculating combined metrics...")
    df, df2 = load()
    calc_time_start = time.time()
    kva_id_unique, pos_id_unique = mt.uniqueness_check(df, df2)
    metrics_combined = {
        "kvarechnung_id_is_unique": kva_id_unique,
        "position_id_is_unique": pos_id_unique
    }
    print("Calculated all combined metrics in "
          f"{round(time.time() - calc_time_start, 2)}s")
    return metrics_combined


@st.cache_data
def compute_positions_over_time():
    """Positionsanzahl pro Auftrag über Zeit – gecached."""
    print("Calculating positions per order over time...")
    df, df2 = load()
    calc_time_start = time.time()
    positions_over_time_df = mt.positions_per_order_over_time(
        df,
        df2,
        time_col="CRMEingangszeit"
    )
    print("Calculated positions over time in "
          f"{round(time.time() - calc_time_start, 2)}s")
    return positions_over_time_df


# CSS
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

# HEADER
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/logo.png")

# NAVIGATION
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


# SEITEN-ROUTING – Lazy Aufruf der Metriken

if selected == "Startseite":
    # Nur hier laden wir die Daten für die Seite (gecached)
    start = time.time()
    df, df2 = load()
    metrics_df1 = compute_metrics_df1()
    metrics_df2 = compute_metrics_df2()
    metrics_combined = compute_metrics_combined()
    page1.show_page(df, df2, metrics_df1, metrics_df2, metrics_combined)
    print("page 1 render time:", round(time.time() - start, 2), "s")

elif selected == "Numerische Daten":
    start = time.time()
    df, df2 = load()
    metrics_df1 = compute_metrics_df1()
    metrics_df2 = compute_metrics_df2()
    metrics_combined = compute_metrics_combined()
    page2.show_page(df, df2, metrics_df1, metrics_df2, metrics_combined)
    print("page 2 render time:", round(time.time() - start, 2), "s")

elif selected == "Textuelle Daten":
    # Seite ist leer
    start = time.time()
    df, df2 = load()
    metrics_df1 = compute_metrics_df1()
    metrics_df2 = compute_metrics_df2()
    metrics_combined = compute_metrics_combined()
    page3.show_page(df, df2, metrics_df1, metrics_df2, metrics_combined)
    print("page 3 render time:", round(time.time() - start, 2), "s")

elif selected == "Plausibilitätscheck":
    start = time.time()
    df, df2 = load()
    metrics_df1 = compute_metrics_df1()
    metrics_df2 = compute_metrics_df2()
    metrics_combined = compute_metrics_combined()
    page4.show_page(df, df2, metrics_df1, metrics_df2, metrics_combined)
    print("page 4 render time:", round(time.time() - start, 2), "s")

elif selected == "Detailansicht":
    # Seite ist leer
    start = time.time()
    df, df2 = load()
    metrics_df1 = compute_metrics_df1()
    metrics_df2 = compute_metrics_df2()
    metrics_combined = compute_metrics_combined()
    page5.show_page(df, df2, metrics_df1, metrics_df2, metrics_combined)
    print("page 5 render time:", round(time.time() - start, 2), "s")
