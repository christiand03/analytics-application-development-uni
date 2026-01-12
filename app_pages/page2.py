import streamlit as st
import pandas as pd
import numpy as np
import metrics as mt

def show_page(df, df2, metrics_df1, metrics_df2, metrics_combined):

    zeitwert_error_series = metrics_df1.get("zeitwert_error_series", mt.check_zeitwert(df))
    zeitwert_error_count = metrics_df1.get("zeitwert_errors_count", 0)
    above_50k_df = metrics_df1.get("above_50k_df", mt.above_50k(df))
    above_50k_count = above_50k_df.size

    auftraege_abgleich = metrics_combined.get("auftraege_abgleich")
    
    # --- KPIs ---
    kpi_cols = st.columns(2)
    with kpi_cols[0]: st.metric(label="Fehleranzahl Zeitwerte", value=zeitwert_error_count)
    with kpi_cols[1]: st.metric(label="Anzahl Aufträge über 50.000€", value=above_50k_count)

    st.markdown("---")

    # --- CHARTS ---
    chart_col1, chart_col2 = st.columns(2)

# Welche Spalten sollten noch rein um die Daten sinnvoll prüfen zu können? Aktuell kein Spaltenname da Series
    with chart_col1:
        st.subheader("Die inkorrekten Zeitwerte:")
        st.dataframe(zeitwert_error_series)

    with chart_col2:
        st.subheader("Aufträge über 50.000€:")
        st.dataframe(above_50k_df)

    st.subheader("Abweichungen Auftragssumme vs. Positionssummen:")
    st.dataframe(auftraege_abgleich)