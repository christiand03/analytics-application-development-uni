import time
import streamlit as st
import duckdb
from streamlit_option_menu import option_menu
from app_pages import page1, page2, page3, page4, page5

start_global = time.time()
st.set_page_config(
    page_title="Data Quality Dashboard",
    page_icon="assets/favicon.png",
    layout="wide"
)

@st.cache_resource
def get_db_connection():
    """Establishes a read-only connection to the DuckDB database."""
    DB_PATH = "resources/dashboard_data.duckdb"
    con = duckdb.connect(DB_PATH, read_only=True)
    return con


@st.cache_data
def compute_metrics_df1():
    print("Loading metrics for df1 (Auftragsdaten) from DB...")
    start_time = time.time()

    con = get_db_connection()
    scalars = con.execute("SELECT * FROM scalar_metrics").df().iloc[0]

    null_ratios_cols = con.execute("SELECT * FROM metric_null_ratios_per_column").df()
    
    test_data_df = con.execute("SELECT * FROM metric_test_data_entries").df()

    plausi_df = con.execute("SELECT * FROM metric_plausibility_diffs_auftragsdaten").df()

    grouped_col_ratios_df1 = con.execute("SELECT * FROM metric_cleanliness_cols_grouped_auftragsdaten").df()
    
    row_ratios_df = con.execute("SELECT * FROM metric_cleanliness_rows_grouped_auftragsdaten").df()
    grouped_row_ratios_df1 = row_ratios_df.set_index('Kundengruppe')['row_null_ratio']

    proforma_df = con.execute("SELECT * FROM metric_proforma").df()

    above_50k_df = con.execute("SELECT * FROM metric_above_50k").df()

    zeitwert_df = con.execute("SELECT * FROM metric_zeitwert_errors").df()

    error_freq_df = con.execute("SELECT * FROM metric_error_heatmap").df()

    handwerker_outliers = con.execute("SELECT * FROM metric_handwerker_outliers").df()

    fn_stats_df1 = con.execute("SELECT * FROM metric_fn_stats_df1").df()
    fn_details_df1 = con.execute("SELECT * FROM metric_fn_details_df1").df()
    fn_count_df = fn_stats_df1['Fehler'].sum()
    semantic_mismatches = con.execute("SELECT * FROM metric_semantic_mismatches").df()

    empty_orders_df = con.execute("SELECT * FROM metric_empty_orders_dataframe").df()
    
    outliers_by_damage = con.execute("SELECT * FROM metric_outliers_by_damage").df()


    metrics_df1 = {
        "row_count": scalars['count_total_orders'],
        "null_ratio_cols": null_ratios_cols,
        "null_ratio_rows": scalars['null_row_ratio_orders'],
        "test_kundengruppen_anzahl": scalars['count_test_data_rows'],
        "test_data_df": test_data_df,
        "plausi_forderung_einigung_df": plausi_df,
        "plausi_forderung_einigung_count": scalars['count_plausibility_errors_df'],
        "plausi_forderung_einigung_avg_diff": scalars['avg_plausibility_diff_df'],
        "grouped_col_ratios": grouped_col_ratios_df1,
        "grouped_row_ratios": grouped_row_ratios_df1,
        "proforma_belege_df": proforma_df,
        "proforma_belege_count": scalars['count_proforma_receipts'],
        "above_50k_df": above_50k_df,
        "zeitwert_error_df": zeitwert_df,
        "zeitwert_errors_count": len(zeitwert_df),
        "error_frequency_weekday_hour": error_freq_df,
        "false_negative": fn_count_df,
        "handwerker_gewerke_outlier": handwerker_outliers,
        "false_negative_stats": fn_stats_df1,
        "false_negative_details": fn_details_df1,
        "empty_orders_count": scalars['count_empty_orders'],
        "mismatched_entries": semantic_mismatches,
        "empty_orders_df": empty_orders_df,
        "outliers_by_damage": outliers_by_damage
    }
    
    print(f"Loaded metrics for df1 in {round(time.time() - start_time, 2)}s")
    return metrics_df1


@st.cache_data
def compute_metrics_df2():
    print("Loading metrics for df2 (Positionsdaten) from DB...")
    start_time = time.time()
    
    con = get_db_connection()
    scalars = con.execute("SELECT * FROM scalar_metrics").df().iloc[0]

    plausi_df2 = con.execute("SELECT * FROM metric_plausibility_diffs_positionsdaten").df()

    position_counts_df = con.execute("SELECT * FROM metric_position_count_positionsdaten").df()

    fn_stats_df2 = con.execute("SELECT * FROM metric_fn_stats_df2").df()
    fn_details_df2 = con.execute("SELECT * FROM metric_fn_details_df2").df()
    disc_stats = con.execute("SELECT * FROM metric_discount_stats").df()
    disc_details = con.execute("SELECT * FROM metric_discount_details").df()
    null_ratio_cols = con.execute("SELECT * FROM metric_cleanliness_cols_ungrouped_positionsdaten").df()


    metrics_df2 = {
        "row_count": scalars['count_total_positions'],
        "null_ratio_cols": null_ratio_cols,
        "null_ratio_rows": scalars['null_row_ratio_positions'] if 'null_row_ratio_positions' in scalars else 0,
        "discount_check_errors": scalars['count_discount_logic_errors'],
        "position_counts_per_rechnung": position_counts_df,
        "plausi_forderung_einigung_count": scalars["count_plausibility_errors_df2"], 
        "plausi_forderung_einigung_avg_diff": scalars["avg_plausibility_diff_df2"],
        "false_negative_stats": fn_stats_df2,
        "false_negative_details": fn_details_df2,
        "discount_stats": disc_stats,
        "discount_details": disc_details,
        "plausi_forderung_einigung_df2": plausi_df2
    }

    print(f"Loaded metrics for df2 in {round(time.time() - start_time, 2)}s")
    return metrics_df2


@st.cache_data
def compute_metrics_combined():
    print("Loading combined metrics from DB...")
    start_time = time.time()
    
    con = get_db_connection()
    scalars = con.execute("SELECT * FROM scalar_metrics").df().iloc[0]
    auftraege_abgleich_df = con.execute("SELECT * FROM metric_order_pos_mismatch").df()

    metrics_combined = {
        "kvarechnung_id_is_unique": bool(scalars['is_unique_kva_id']),
        "kvarechnung_nummer_land_is_unique": bool(scalars['is_unique_kva_nr_per_land']),
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
    df_pos_time = con.execute("SELECT * FROM metric_positions_over_time").df()
    
    print(f"Loaded positions over time in {round(time.time() - start_time, 2)}s")
    return df_pos_time

@st.cache_data
def compute_comparison_metrics():
    print("Loading comparison metrics from DB...")
    start_time = time.time()
    
    con = get_db_connection()
    comparison_df = con.execute("SELECT * FROM metric_comparison").df()
    
    print(f"Loaded comparison metrics in {round(time.time() - start_time, 2)}s")
    return comparison_df

@st.cache_data
def compute_issues_df():
    print("Loading issues metrics from DB...")
    start_time = time.time()
    con = get_db_connection()
    issues_df = con.execute("SELECT * FROM issues").df().iloc[0]
    print(f"Loaded issues metrics in {round(time.time() - start_time, 2)}s")
    return issues_df

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
metrics_df1 = compute_metrics_df1()
metrics_df2 = compute_metrics_df2()
metrics_combined = compute_metrics_combined()
comparison_df = compute_comparison_metrics()
issues_df = compute_issues_df()
print(f"Global data loaded in {round(time.time() - start_global, 2)}s")

if selected == "Startseite":
    start = time.time()
    pos_time = compute_positions_over_time()
    page1.show_page(metrics_df1, metrics_df2, metrics_combined, pos_time, comparison_df, issues_df)
    print("page 1 render time:", round(time.time() - start, 2), "s")

elif selected == "Numerische Daten":
    start = time.time()
    page2.show_page(metrics_df1, metrics_df2, metrics_combined, comparison_df, issues_df)
    print("page 2 render time:", round(time.time() - start, 2), "s")

elif selected == "Textuelle Daten":
    start = time.time()
    page3.show_page(metrics_df1, metrics_df2, comparison_df, issues_df)
    print("page 3 render time:", round(time.time() - start, 2), "s")

elif selected == "Plausibilitätscheck":
    start = time.time()
    page4.show_page(metrics_df1, metrics_df2, comparison_df, issues_df)
    print("page 4 render time:", round(time.time() - start, 2), "s")

elif selected == "Data Drift":
    start = time.time()
    page5.show_page()
    print("page 5 render time:", round(time.time() - start, 2), "s")