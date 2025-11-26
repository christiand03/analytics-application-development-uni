import streamlit as st
import pandas as pd
import numpy as np

# --- 1. Daten laden ---
@st.cache_data
def load_data():
    dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
    df = pd.DataFrame({
        'datum': dates,
        # Wir bauen einen künstlichen "Drift" ein, damit man im Chart was sieht
        # Der Umsatz steigt langsam an, die Varianz (Std) wird höher
        'umsatz': np.linspace(200, 800, len(dates)) + np.random.normal(0, 50, len(dates)),
        'kunden': np.random.randint(10, 50, size=len(dates))
    })
    return df

df = load_data()

# --- 2. Helper Funktionen ---
def filterby_timeframe(input_df, start_date, end_date):
    start_ts = pd.to_datetime(start_date)
    end_ts = pd.to_datetime(end_date)
    date_mask = (input_df['datum'] >= start_ts) & (input_df['datum'] <= end_ts)
    return input_df.loc[date_mask]

def get_drift_stats(input_df, frequency):
    """
    Berechnet Statistiken (Mean, Median, Std) gruppiert nach Frequenz
    für die Charts.
    """
    # Gruppieren nach Zeit
    grouper = pd.Grouper(key='datum', freq=frequency)
    
    # Wir berechnen mehrere Metriken gleichzeitig
    stats_df = input_df.groupby(grouper)[['umsatz', 'kunden']].agg(['mean', 'median', 'std', 'min', 'max'])
    
    # Die Spalten sind jetzt ein MultiIndex (z.B. umsatz -> mean). 
    # Wir machen sie flach für einfacheres Plotten: 'umsatz_mean', 'umsatz_std' etc.
    stats_df.columns = ['_'.join(col).strip() for col in stats_df.columns.values]
    
    return stats_df

def slicing(input_df, frequency):
    """
    Erstellt die einzelnen Slices für die Detail-Ansicht (Expanders)
    """
    try:
        grouping = pd.Grouper(key='datum', freq=frequency)
        grouped = input_df.groupby(grouping)

        slices = {}
        for name, group in grouped:
            if not group.empty:
                label = name.strftime('%Y-%m-%d') 
                slices[label] = group
        return slices
    except Exception as e:
        st.error(f"Fehler beim Slicing: {e}")
        return {}

# --- 3. UI & Logik ---
st.title("📉 Data Drift Dashboard")

# Filter Einstellungen
min_avail_date = df['datum'].min().date()
max_avail_date = df['datum'].max().date()

with st.sidebar:
    st.header("Filter")
    start_date = st.date_input("Start Datum", value=min_avail_date, min_value=min_avail_date, max_value=max_avail_date)
    end_date = st.date_input("End Datum", value=max_avail_date, min_value=min_avail_date, max_value=max_avail_date)
    
    freq_options = {
        "Woche": "W-MON",
        "Monat": "ME",     
        "Quartal": "QE",   
        "Jahr": "YE"       
    }
    freq_selection = st.selectbox("Zeitraum-Slice", options=list(freq_options.keys()))
    freq_code = freq_options[freq_selection]

# Daten filtern
df_filtered = filterby_timeframe(df, start_date, end_date)

if df_filtered.empty:
    st.warning("Keine Daten im gewählten Zeitraum.")
else:
    # --- TEIL A: Globale Drift Charts ---
    st.header(f"1. Drift Analyse (Zeitraum: {freq_selection})")
    
    # Statistiken über die Zeit berechnen
    drift_df = get_drift_stats(df_filtered, freq_code)
    
    tab1, tab2 = st.tabs(["Umsatz Drift", "Kunden Drift"])
    
    with tab1:
        st.subheader("Umsatz: Mittelwert & Median über Zeit")
        # Wir zeigen Mean und Median in einem Chart
        st.line_chart(drift_df[['umsatz_mean', 'umsatz_median']])
        
        st.subheader("Umsatz: Volatilität (Standardabweichung)")
        st.area_chart(drift_df[['umsatz_std']], color="#ffaa00")

    with tab2:
        st.subheader("Kunden: Mittelwert & Median über Zeit")
        st.line_chart(drift_df[['kunden_mean', 'kunden_median']])
        
        st.subheader("Kunden: Volatilität (Standardabweichung)")
        st.area_chart(drift_df[['kunden_std']], color="#00aa00")

    # --- TEIL B: Detail Slices ---
    st.header("2. Detail Slices & Statistik")
    
    slices = slicing(df_filtered, freq_code)
    
    if slices:
        for slice_name, slice_df in slices.items():
            # Wir berechnen die Statistiken für diesen spezifischen Slice
            stats = slice_df[['umsatz', 'kunden']].describe()
            
            # Quick Stats für den Expander-Titel berechnen
            u_mean = stats.loc['mean', 'umsatz']
            k_mean = stats.loc['mean', 'kunden']
            
            with st.expander(f"🗓️ {slice_name} | Ø Umsatz: {u_mean:.2f} | Ø Kunden: {k_mean:.1f}"):
                col_left, col_right = st.columns([1, 2])
                
                with col_left:
                    st.markdown("**Statistische Kennzahlen:**")
                    # describe() gibt einen schönen kleinen DataFrame zurück
                    st.dataframe(stats)
                
                with col_right:
                    st.markdown("**Verteilung (Histogramm):**")
                    # Kleines Histogramm für diesen Slice, um die Verteilung zu sehen
                    # Wir nehmen Umsatz als Beispiel
                    hist_values = np.histogram(slice_df['umsatz'], bins=10)[0]
                    st.bar_chart(hist_values)