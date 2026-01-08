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
        # Returns a Series indexed by column name for easy dict-like access
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
        # Load Complex Metrics Tables
        null_ratios_cols = con.execute("SELECT * FROM metric_null_ratios_per_column").df()
        
        # Test Data: If table is empty, return 0/Empty DataFrame logic handled by scalars + empty DF
        test_data_df = con.execute("SELECT * FROM metric_test_data_entries").df()
        
        # Statistics: Convert back to nested dict structure expected by Page 2
        # DB Table format: [column_name, mean, std, ...]
        stats_df = con.execute("SELECT * FROM metric_numeric_stats_auftragsdaten").df()
        statistiken_num = stats_df.set_index('column_name').T.to_dict()

        # Plausibility: Convert DF column back to Series
        plausi_df = con.execute("SELECT * FROM metric_plausibility_diffs_auftragsdaten").df()
        plausi_diff_list = plausi_df['differenz_eur'] if not plausi_df.empty else pd.Series(dtype=float)

        # Cleanliness Grouped: 
        grouped_col_ratios_df1 = con.execute("SELECT * FROM metric_cleanliness_cols_grouped_auftragsdaten").df()
        
        # Row Ratios Grouped: Convert DF back to Series expected by charts
        row_ratios_df = con.execute("SELECT * FROM metric_cleanliness_rows_grouped_auftragsdaten").df()
        grouped_row_ratios_df1 = row_ratios_df.set_index('Kundengruppe')['row_null_ratio']

        # Proforma
        proforma_df = con.execute("SELECT * FROM metric_proforma").df()

        # Above 50k
        above_50k_df = con.execute("SELECT * FROM metric_above_50k").df()

        # Zeitwert Errors: Convert to Series
        zeitwert_df = con.execute("SELECT * FROM metric_zeitwert_errors").df()
        zeitwert_errors_series = zeitwert_df['zeitwert_diff'] if not zeitwert_df.empty else pd.Series(dtype=float)

        # Heatmap
        error_freq_df = con.execute("SELECT * FROM metric_error_heatmap").df()

        # Handwerker Outliers
        handwerker_outliers = con.execute("SELECT * FROM metric_handwerker_outliers").df()
        
        # Semantic Mismatches (previously commented out, now available in DB)
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
        # Statistics: Convert back to dict
        stats_df2 = con.execute("SELECT * FROM metric_numeric_stats_positionsdaten").df()
        statistiken_num = stats_df2.set_index('column_name').T.to_dict()
        
        # Plausibility
        plausi_df2 = con.execute("SELECT * FROM metric_plausibility_diffs_positionsdaten").df()
        plausi_diff_list = plausi_df2['differenz_eur'] if not plausi_df2.empty else pd.Series(dtype=float)

        # Position Counts (This logic was inside the DB script used for merging, 
        # but if page2 needs the aggregation dataframe, we might need to query positionsdaten.
        # Assuming page just needs stats or scalars mostly, but here is the count logic if needed re-derived
        # or if specific metrics required it. Based on `metrics_df2` keys, we need:
        # "position_counts_per_rechnung". 
        # Note: The DB script used `mt.position_count(df2)` to merge into `auftragsdaten`, 
        # but didn't explicitly save the simple `position_count` DF as a standalone metric table.
        # We can quickly aggregate it via SQL here since it's fast.)
        position_counts_df = con.execute("""
            SELECT KvaRechnung_ID, COUNT(Position_ID) as PositionsAnzahl 
            FROM positionsdaten 
            GROUP BY KvaRechnung_ID
        """).df()

    finally:
        con.close()

    metrics_df2 = {
        "row_count": scalars['count_total_positions'],
        "null_ratio_cols": pd.read_sql("SELECT * FROM metric_cleanliness_cols_ungrouped_positionsdaten", get_db_connection()), # Loading ad-hoc or from ungrouped table
        "null_ratio_rows": scalars['null_ratio_positions'] if 'null_ratio_positions' in scalars else 0, # Note: scalar name in DB script was null_ratio_positions? No, script says `null_ratio_positions = mt.ratio...` but scalar key was NOT explicitly `null_ratio_positions`? 
        # Checking DB Script: key was 'null_ratio_positions' variable, but stored in df_scalars? 
        # Wait, the DB script creates `null_ratio_orders` and `null_ratio_positions` but in `kpi_data` dictionary:
        # 'null_row_ratio_orders': ... but I don't see 'null_row_ratio_positions' in the kpi_data dict in your snippet!
        # I will calculate it here quickly to be safe or assume it's 0 if not found.
        # FIX: The provided DB script does NOT save null_ratio_rows for df2 in scalars. 
        # I will compute it via SQL quickly.
        "statistiken_num": statistiken_num,
        "discount_check_errors": scalars['count_discount_logic_errors'],
        "position_counts_per_rechnung": position_counts_df,
        "plausi_forderung_einigung_list": plausi_diff_list,
        "plausi_forderung_einigung_count": plausi_diff_list.size, # Approximate if exact count not in scalar
        "plausi_forderung_einigung_avg_diff": plausi_diff_list.mean() if not plausi_diff_list.empty else 0,
        "false_negative": scalars['count_false_negative_df2']
    }
    
    # Fix for missing scalar key in DB script provided:
    # Calculating null ratio rows for positionsdaten on the fly via SQL
    con = get_db_connection()
    total_rows = scalars['count_total_positions']
    # Approximate check for nulls in all columns
    # (Doing this in SQL is tedious for all columns without a loop, 
    # but strictly speaking we can load it from a helper if needed. 
    # For performance, let's assume 0 or calc on loaded DF2)
    # Since we have df2 loaded in 'load()', the page might re-calculate or we can use the loaded DF.
    # To keep this function standalone, let's use the DF from load():
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
        # Order/Position Mismatch
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