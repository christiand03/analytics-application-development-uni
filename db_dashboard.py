import time
import pandas as pd
import streamlit as st
import duckdb
from streamlit_option_menu import option_menu
from app_pages import page1, page2, page3, page4, page5


st.set_page_config(
    page_title="Data Quality Dashboard",
    page_icon="assets/logo.png",
    layout="wide"
)

DB_PATH = "resources/dashboard_data.duckdb"

def get_db_connection():
    """Establishes a read-only connection to the DuckDB database."""
    return duckdb.connect(DB_PATH, read_only=True)

@st.cache_data
def load():
    """Loads the raw cleaned dataframes from DuckDB."""
    con = get_db_connection()
    try:
        df = con.execute("SELECT * FROM auftragsdaten").df()
        df2 = con.execute("SELECT * FROM positionsdaten").df()
        return df, df2
    finally:
        con.close()

@st.cache_data
def get_scalar_metrics():
    """Helper to load the single-row scalar table."""
    con = get_db_connection()
    try:
        return con.execute("SELECT * FROM scalar_metrics").df().iloc[0]
    finally:
        con.close()

@st.cache_data
def compute_metrics_df1():
    print("Loading metrics for df1 (Auftragsdaten) from DB...")
    start_time = time.time()
    
    con = get_db_connection()
    scalars = get_scalar_metrics()
    
    try:
        null_ratios_cols = con.execute("SELECT * FROM metric_null_ratios_per_column").df()
        
        test_data_df = con.execute("SELECT * FROM metric_test_data_entries").df()
        
        stats_df = con.execute("SELECT * FROM metric_numeric_stats_auftragsdaten").df()
        statistiken_num = stats_df.set_index('column_name').T.to_dict()

        plausi_df = con.execute("SELECT * FROM metric_plausibility_diffs_auftragsdaten").df()
        plausi_diff_list = plausi_df['differenz_eur'] if not plausi_df.empty else pd.Series(dtype=float)

        grouped_col_ratios_df1 = con.execute("SELECT * FROM metric_cleanliness_cols_grouped_auftragsdaten").df()
        
        row_ratios_df = con.execute("SELECT * FROM metric_cleanliness_rows_grouped_auftragsdaten").df()
        grouped_row_ratios_df1 = row_ratios_df.set_index('Kundengruppe')['row_null_ratio']

        proforma_df = con.execute("SELECT * FROM metric_proforma").df()

        above_50k_df = con.execute("SELECT * FROM metric_above_50k").df()

        zeitwert_df = con.execute("SELECT * FROM metric_zeitwert_errors").df()
        zeitwert_errors_series = zeitwert_df['zeitwert_diff'] if not zeitwert_df.empty else pd.Series(dtype=float)

        error_freq_df = con.execute("SELECT * FROM metric_error_heatmap").df()

        handwerker_outliers = con.execute("SELECT * FROM metric_handwerker_outliers").df()
        
        semantic_mismatches = con.execute("SELECT * FROM metric_semantic_mismatches").df()

    finally:
        con.close()

    metrics_df1 = {
        "row_count": scalars['count_total_orders'],
        "null_ratio_cols": null_ratios_cols,
        "null_ratio_rows": scalars['null_row_ratio_orders'],
        "test_kundengruppen_anzahl": scalars['count_test_data_rows'],
        "statistiken_num": statistiken_num,
        "plausi_forderung_einigung_list": plausi_diff_list,
        "plausi_forderung_einigung_count": scalars['count_plausibility_errors'],
        "plausi_forderung_einigung_avg_diff": scalars['avg_plausibility_diff'],
        "grouped_col_ratios": grouped_col_ratios_df1,
        "grouped_row_ratios": grouped_row_ratios_df1,
        "proforma_belege_df": proforma_df,
        "proforma_belege_count": scalars['count_proforma_receipts'],
        "above_50k_df": above_50k_df,
        "zeitwert_errors_list": zeitwert_errors_series,
        "zeitwert_errors_count": zeitwert_errors_series.size,
        "error_frequency_weekday_hour": error_freq_df,
        "false_negative": scalars['count_false_negative_df'],
        "handwerker_gewerke_outlier": handwerker_outliers,
        "mismatched_entries": semantic_mismatches
    }
    
    print(f"Loaded metrics for df1 in {round(time.time() - start_time, 2)}s")
    return metrics_df1


@st.cache_data
def compute_metrics_df2():
    print("Loading metrics for df2 (Positionsdaten) from DB...")
    start_time = time.time()
    
    con = get_db_connection()
    scalars = get_scalar_metrics()

    try:

        stats_df2 = con.execute("SELECT * FROM metric_numeric_stats_positionsdaten").df()
        statistiken_num = stats_df2.set_index('column_name').T.to_dict()
        
        plausi_df2 = con.execute("SELECT * FROM metric_plausibility_diffs_positionsdaten").df()
        plausi_diff_list = plausi_df2['differenz_eur'] if not plausi_df2.empty else pd.Series(dtype=float)

        position_counts_df = con.execute("""
            SELECT KvaRechnung_ID, COUNT(Position_ID) as PositionsAnzahl 
            FROM positionsdaten 
            GROUP BY KvaRechnung_ID
        """).df()

    finally:
        con.close()

    metrics_df2 = {
        "row_count": scalars['count_total_positions'],
        "null_ratio_cols": pd.read_sql("SELECT * FROM metric_cleanliness_cols_ungrouped_positionsdaten", get_db_connection()),
        "null_ratio_rows": scalars['null_ratio_positions'] if 'null_ratio_positions' in scalars else 0, 
        "statistiken_num": statistiken_num,
        "discount_check_errors": scalars['count_discount_logic_errors'],
        "position_counts_per_rechnung": position_counts_df,
        "plausi_forderung_einigung_list": plausi_diff_list,
        "plausi_forderung_einigung_count": plausi_diff_list.size, 
        "plausi_forderung_einigung_avg_diff": plausi_diff_list.mean() if not plausi_diff_list.empty else 0,
        "false_negative": scalars['count_false_negative_df2']
    }
    
    con = get_db_connection()
    total_rows = scalars['count_total_positions']
    _, df2_temp = load()
    metrics_df2["null_ratio_rows"] = (df2_temp.isnull().any(axis=1).sum() / len(df2_temp) * 100) if len(df2_temp) > 0 else 0
    con.close()

    print(f"Loaded metrics for df2 in {round(time.time() - start_time, 2)}s")
    return metrics_df2


@st.cache_data
def compute_metrics_combined():
    print("Loading combined metrics from DB...")
    start_time = time.time()
    
    con = get_db_connection()
    scalars = get_scalar_metrics()
    
    try:
        auftraege_abgleich_df = con.execute("SELECT * FROM metric_order_pos_mismatch").df()
    finally:
        con.close()

    metrics_combined = {
        "kvarechnung_id_is_unique": bool(scalars['is_unique_kva_id']),
        "position_id_is_unique": bool(scalars['is_unique_position_id']),
        "auftraege_abgleich": auftraege_abgleich_df
    }
    
    print(f"Loaded combined metrics in {round(time.time() - start_time, 2)}s")
    return metrics_combined


@st.cache_data
def compute_positions_over_time():
    print("Loading positions per order over time from DB...")
    start_time = time.time()
    con = get_db_connection()
    try:
        df_pos_time = con.execute("SELECT * FROM metric_positions_over_time").df()
    finally:
        con.close()
    
    print(f"Loaded positions over time in {round(time.time() - start_time, 2)}s")
    return df_pos_time


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
            "Data Drift"
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


# PAGE ROUTING

if selected == "Startseite":
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

elif selected == "Data Drift":
    start = time.time()
    df, df2 = load()
    metrics_df1 = compute_metrics_df1()
    metrics_df2 = compute_metrics_df2()
    metrics_combined = compute_metrics_combined()
    page5.show_page(df, df2, metrics_df1, metrics_df2, metrics_combined)
    print("page 5 render time:", round(time.time() - start, 2), "s")