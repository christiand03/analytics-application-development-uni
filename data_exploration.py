import pandas as pd
import streamlit as st
import time

start_time = time.time()
@st.cache_data
def load():
    
    df = pd.read_parquet("C:/Uni/Analytics Application Development/Projekt/Auftragsdaten")
    df2 = pd.read_parquet("C:/Uni/Analytics Application Development/Projekt/Positionsdaten")
    return df, df2

df, df2 = load()
load_time = time.time()
loading_time = load_time - start_time
st.write(f"Daten geladen. Es hat {loading_time:.4f} Sekunden gedauert.")

#df = df.sort_values(by='KvaRechnung_Nummer')
#df2 = df2.sort_values(by='KvaRechnung_Nummer')
a= df.head(100)
b = df2.head(100)

st.write("Auftragsdaten")
st.dataframe(a)
st.write("Positionsdaten")
st.dataframe(b)

auftragsdaten_numeric_columns = ["Forderung_Netto", "Empfehlung_Netto", "Einigung_Netto", "DH_ID", "Differenz_vor_Zeitwert_Netto"]
for column in auftragsdaten_numeric_columns:
    st.write(f"Statistische Daten für {column}:")
    st.write(df[column].describe())

processing_time = time.time() - load_time
st.write(f"Datenverarbeitung dauerte: {processing_time:.4f} Sekunden")

