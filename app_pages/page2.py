import streamlit as st
import pandas as pd
import numpy as np

def show_page():

    # --- KPIs ---
    kpi_cols = st.columns(6)
    with kpi_cols[0]: st.metric(label="Verkäufe (EUR)", value="15.4k", delta="2.1k")
    with kpi_cols[1]: st.metric(label="Retourenquote", value="8.1%", delta="0.5%")
    with kpi_cols[2]: st.metric(label="Warenkorbwert", value="82.50", delta="-2.30")
    with kpi_cols[3]: st.metric(label="Conversion Rate", value="4.2%", delta="0.8%")
    with kpi_cols[4]: st.metric(label="Kunden-Zufriedenheit", value="4.6/5", delta="0.1")
    with kpi_cols[5]: st.metric(label="Lagerbestand", value="2.1M", delta="-50k")

    st.markdown("---")

    # --- CHARTS ---
    # Hier verwenden wir andere Chart-Typen zur Demonstration
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Umsatz nach Kategorie")
        # Dummy-Daten für Bar-Chart
        chart_data = pd.DataFrame(
            np.random.rand(5, 3),
            columns=["Kategorie A", "Kategorie B", "Kategorie C"]
        )
        st.bar_chart(chart_data)

    with chart_col2:
        st.subheader("Verteilung der Kundensegmente")
        # Dummy-Daten für Area-Chart
        chart_data2 = pd.DataFrame(
            np.random.randn(20, 3),
            columns=['Segment X', 'Segment Y', 'Segment Z']
        )
        st.area_chart(chart_data2)