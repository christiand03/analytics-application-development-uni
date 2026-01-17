import time
import pandas as pd
import streamlit as st
import metrics as mt
from streamlit_option_menu import option_menu
from app_pages import page1, page2, page3, page4, page5

st.set_page_config(
    page_title="Data Quality Dashboard",
    page_icon="assets/favicon.png",
    layout="wide"
)
start_global = time.time()
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
    plausi_diff_df, plausi_count, plausi_avg = mt.plausibilitaetscheck_forderung_einigung(df)
    print("Calculated plausi_diff_list, plausi_count, plausi_avg in "
          f"{round(time.time() - calc_time_start, 2)}s")

    calc_time_start = time.time()
    zeitwert_errors_df = mt.check_zeitwert(df)
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
    df_added = mt.handwerker_gewerke_outlier(df)
    df_true = df_added[df_added['is_outlier'] == True].copy()
    df_true['Check_Result'] = mt.check_keywords(df_true)

    print("Calculated craftsman/craft comparison in "
          f"{round(time.time() - calc_time_start, 2)}s")
    
    calc_time_start = time.time()
    fn_stats_df, fn_details_df = mt.false_negative_df1(df)
    fn_count_df = fn_stats_df['Fehler'].sum()
    print("Calculated fn_stats, fn_details in "
          f"{round(time.time() - calc_time_start, 2)}s")

    calc_time_start = time.time()
    metrics_df1 = {
        "row_count": mt.count_rows(df),
        "null_ratio_cols": mt.ratio_null_values_column(df),
        "null_ratio_rows": mt.ratio_null_values_rows(df),
        "test_kundengruppen_anzahl": mt.Kundengruppe_containing_test(df),
        "test_data_df": mt.Kundengruppe_containing_test(df, return_frame=True),
        "plausi_forderung_einigung_df": plausi_diff_df,
        "plausi_forderung_einigung_count": plausi_count,
        "plausi_forderung_einigung_avg_diff": plausi_avg,
        "grouped_col_ratios": grouped_col_ratios_df1,
        "grouped_row_ratios": grouped_row_ratios_df1,
        "proforma_belege_df": proforma_df,
        "proforma_belege_count": proforma_count,
        "above_50k_df": mt.above_50k(df),
        "zeitwert_error_df": zeitwert_errors_df,
        "zeitwert_errors_count": len(zeitwert_errors_df),
        "error_frequency_weekday_hour": error_freq_df,
        "false_negative": fn_count_df,
        "false_negative_stats": fn_stats_df,
        "false_negative_details": fn_details_df,
        "mismatched_entries": mt.mismatched_entries(df),
        "handwerker_gewerke_outlier": df_true,
        "empty_orders_count": mt.empty_orders(df)
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
    
    plausi_diff_df, plausi_count, plausi_avg = mt.plausibilitaetscheck_forderung_einigung(df2)
    print("Calculated plausi_diff_list, plausi_count, plausi_avg in "
          f"{round(time.time() - calc_time_start, 2)}s")
    
    calc_time_start = time.time()
    disc_stats, disc_details = mt.discount_details(df2)
    print("Calculated discount_stats, discount_details in "
          f"{round(time.time() - calc_time_start, 2)}s")
    
    calc_time_start = time.time()
    fn_stats_df2, fn_details_df2 = mt.false_negative_df2(df2)
    print("Calculated fn_stats, fn_details in "
          f"{round(time.time() - calc_time_start, 2)}s")
    
    metrics_df2 = {
        "row_count": mt.count_rows(df2),
        "null_ratio_cols": mt.ratio_null_values_column(df2),
        "null_ratio_rows": mt.ratio_null_values_rows(df2),
        "discount_check_errors": mt.discount_check(df2), #
        "position_counts_per_rechnung": mt.position_count(df2),
        "plausi_forderung_einigung_df2": plausi_diff_df,
        "plausi_forderung_einigung_count": plausi_count,
        "plausi_forderung_einigung_avg_diff": plausi_avg,
        "false_negative_stats": fn_stats_df2,
        "false_negative_details": fn_details_df2,
        "discount_stats": disc_stats,
        "discount_details": disc_details,
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
    auftraege_abgleich = mt.abgleich_auftraege(df, df2)
    metrics_combined = {
        "kvarechnung_id_is_unique": kva_id_unique,
        "position_id_is_unique": pos_id_unique,
        "auftraege_abgleich": auftraege_abgleich
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

@st.cache_data
def compute_issues_df():

    zeitwert = metrics_df1.get("zeitwert_errors_count")
    df_above_50k = metrics_df1.get("above_50k_df")
    df_semantic = metrics_df1.get("mismatched_entries")
    test_data_count = metrics_df1.get("test_kundengruppen_anzahl")
    df_mismatch = metrics_combined.get("auftraege_abgleich")
    df_outliers_true = metrics_df1.get("handwerker_gewerke_outlier")
    plausibility_error_count_df = metrics_df1.get("plausi_forderung_einigung_count")
    plausibility_error_count_df2 = metrics_df1.get("plausi_forderung_einigung_count")
    discount_logic_errors = metrics_df2.get("discount_check_errors")
    proforma_count = metrics_df1.get("proforma_belege_count")
    fn_details1 = metrics_df1.get("false_negative_details")
    fn_details2 = metrics_df2.get("false_negative_details")
    
    numeric_issues = zeitwert + len(df_above_50k) + len(df_mismatch)
    text_issues = test_data_count + len(df_outliers_true) + len(df_semantic)
    plausi_issues = plausibility_error_count_df + plausibility_error_count_df2 + discount_logic_errors + proforma_count + len(fn_details1) + len(fn_details2)
    overall_issues = numeric_issues + text_issues + plausi_issues

    issues = {
        'numeric_issues': [numeric_issues],
        'text_issues': [text_issues],
        'plausi_issues': [plausi_issues],
        'overall_issues': [overall_issues],
        'count_zeitwert_errors': [zeitwert],
        'count_above_50k': [len(df_above_50k)],
        'count_handwerker_outliers': [len(df_outliers_true)],
        'count_semantic_outliers': [len(df_semantic)],
        'count_abweichung_summen': [len(df_mismatch)],
        'count_plausibility_errors_df': [plausibility_error_count_df],
        'count_plausibility_errors_df2': [plausibility_error_count_df2],
        'count_false_negative_df': [len(fn_details1)],
        'count_false_negative_df2': [len(fn_details2)],
    }

    df_issues = pd.DataFrame(issues)

    return df_issues


### Static Data to get the dashboard to load (the standard dashboard.py doesnt support the trend analysis) 
@st.cache_data
def compute_comparison_metrics():
    data = {
    'Metric': [
        'avg_plausibility_diff_df', 
        'avg_plausibility_diff_df2', 
        'count_above_50k', 
        'count_abweichung_summen', 
        'count_discount_logic_errors'
    ],
    'Current_Value': [
        1560.530884, 
        406.184998, 
        306.000000, 
        34581.000000, 
        22110.000000
    ],
    'Old_Value': [
        1560.530884, 
        406.184998, 
        306.000000, 
        34581.000000, 
        22110.000000
    ],
    'Percent_Change': [0.0, 0.0, 0.0, 0.0, 0.0]
}

    # Define the specific indices from your example
    indices = [10, 13, 21, 24, 15]

    df = pd.DataFrame(data, index=indices)

    return df




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


# SEITEN-ROUTING 
metrics_df1 = compute_metrics_df1()
metrics_df2 = compute_metrics_df2()
metrics_combined = compute_metrics_combined()
issues_df = compute_issues_df()
issues_df = issues_df.iloc[0]
comparison_df = compute_comparison_metrics()
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
