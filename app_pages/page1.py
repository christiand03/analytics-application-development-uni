import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import norm

def show_page():

    # --- KPI-BEREICH (6 Kacheln) ---
    kpi_cols = st.columns(6)
    
    with kpi_cols[0]:
        st.metric(label="Datenqualität", value="98,7%", delta="-0,2%")
    with kpi_cols[1]:
        st.metric(label="Neue Datensätze", value="71")
    with kpi_cols[2]:
        st.metric(label="Anzahl fehlerhafte Daten", value="31", delta="15", delta_color="inverse")
    with kpi_cols[3]:
        st.metric(label="Fehlerquote", value="1.5%", delta="-0,3%", delta_color="inverse")
    with kpi_cols[4]:
        st.metric(label="Ladezeit (s)", value="0.8", delta="-5%", delta_color="inverse")
    with kpi_cols[5]:
        st.metric(label="Test", value="31", delta="+15", delta_color="inverse")
    
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True) # Fügt einen kleineren, kontrollierten Abstand hinzu

    # --- CHART-BEREICH (2 große Charts nebeneinander) ---
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Chart im Stil der Skizze 1")
        
        filter_col, graph_col = st.columns([1, 4]) 

        with filter_col:
            st.markdown("##### Filter")
            st.selectbox("Zeitraum", ["Letzte 7 Tage", "Letzter Monat", "Letztes Quartal"], key="p1_sb1")
            st.slider("Glättungsfaktor", 0.0, 1.0, 0.5, key="p1_sl1")
        
        with graph_col:
            x = np.linspace(0, 10, 100)
            y = np.sin(x) + x/5 + np.random.randn(100) * 0.1
            chart_data = pd.DataFrame(y, index=x)
            st.line_chart(chart_data, use_container_width=True)

    with chart_col2:
        st.subheader("Chart im Stil der Skizze 2")

        filter_col, graph_col = st.columns([1, 4])

        with filter_col:
            st.markdown("##### Filter")
            st.selectbox("Kategorie", ["A", "B", "C"], key="p1_sb2")
            st.date_input("Datum wählen", key="p1_d1")

        with graph_col:
            x = np.linspace(-5, 5, 100)
            y = norm.pdf(x, 0, 1.5)
            chart_data2 = pd.DataFrame(y, index=x)
            st.line_chart(chart_data2, use_container_width=True)