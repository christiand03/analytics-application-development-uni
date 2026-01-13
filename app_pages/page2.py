import streamlit as st
import pandas as pd

def show_page(metrics_df1, metrics_df2, metrics_combined, comparison_df=None):

    # Helperfunction to get delta from comparison_df
    def get_delta(metric_name):
        if comparison_df is None or comparison_df.empty:
            return None
        
        row = comparison_df[comparison_df['Metric'] == metric_name]
        
        if not row.empty:
            val = row.iloc[0]['Percent_Change']
            return f"{val:+.2f}%"
        return None

    zeitwert_error_df = metrics_df1.get("zeitwert_error_df", pd.NA)
    zeitwert_error_count = metrics_df1.get("zeitwert_errors_count", pd.NA)
    above_50k_df = metrics_df1.get("above_50k_df", pd.NA)
    above_50k_count = above_50k_df.size

    auftraege_abgleich = metrics_combined.get("auftraege_abgleich")
    
    # --- KPIs ---
    kpi_cols = st.columns(2)
    with kpi_cols[0]: st.metric(label="Fehleranzahl Zeitwerte", value=zeitwert_error_count, delta=get_delta("count_zeitwert_errors"), delta_color="inverse")
    with kpi_cols[1]: st.metric(label="Anzahl Aufträge über 50.000€", value=above_50k_count, delta=get_delta("count_above_50k"), delta_color="inverse")

    st.markdown("---")

    # --- CHARTS ---
    chart_col1, chart_col2 = st.columns(2)

# Welche Spalten sollten noch rein um die Daten sinnvoll prüfen zu können? Aktuell kein Spaltenname da Series
    with chart_col1:
        st.subheader("Die inkorrekten Zeitwerte:")
        st.dataframe(zeitwert_error_df)

    with chart_col2:
        st.subheader("Aufträge über 50.000€:")
        st.dataframe(above_50k_df)

    st.subheader("Abweichungen Auftragssumme vs. Positionssummen:")
    st.dataframe(auftraege_abgleich)