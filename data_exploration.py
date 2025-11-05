import pandas as pd
import streamlit as st
import time

start_time = time.time()
@st.cache_data
def load():

    df = pd.read_parquet("resources/Auftragsdaten_konvertiert")
    df2 = pd.read_parquet("resources/Positionsdaten_konvertiert")
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
st.write(df.dtypes)

st.write("Positionsdaten")
st.dataframe(b)
st.write(df2.dtypes)


st.write("-----------------------Auftragsdaten-----------------------")
auftragsdaten_numeric_columns = ["Forderung_Netto", "Empfehlung_Netto", "Einigung_Netto", "Differenz_vor_Zeitwert_Netto"]
for column in auftragsdaten_numeric_columns:
    st.write(f"Statistische Daten für {column}:")
    st.write(df[column].describe())

st.write("-----------------------Positionsdaten-----------------------")
positionsdaten_numeric_columns = ["Menge", "Menge_Einigung", "EP", "EP_Einigung", "Forderung_Netto", "Einigung_Netto"]
for column in positionsdaten_numeric_columns:
    st.write(f"Statistische Daten für {column}:")
    st.write(df2[column].describe())

df_unique = df[["DH_ID", "Land", "Schadenart_Name", "Falltyp_Name", "Gewerk_Name", "Kundengruppe"]]

st.write("------ Unique Values für Auftragsdaten ------")
for col in df_unique.columns:
    
    print(f"--- Tabelle für Spalte: '{col}' ---")
    
    unique_values = df_unique[col].unique()
    tabelle_pro_spalte = pd.DataFrame(unique_values, columns=[col])
    st.dataframe(tabelle_pro_spalte)


df2_unique = df2[["Mengeneinheit", "Menge", "Menge_Einigung", "Bemerkung"]]

st.write("------ Unique Values für Positionsdaten ------")
for col in df2_unique.columns:
    
    print(f"--- Tabelle für Spalte: '{col}' ---")
    
    unique_values = df2_unique[col].unique()
    tabelle_pro_spalte = pd.DataFrame(unique_values, columns=[col])
    st.dataframe(tabelle_pro_spalte)



st.write("------ Value Counts für Auftragsdaten ------")
for col in df.columns:
    print("--- Value Count für Spalte: '{col}' ---")
    st.write(df[col].value_counts())

st.write("------ Value Counts für Positionsdaten ------")
for col in df2.columns:
    print("--- Value Count für Spalte: '{col}' ---")
    st.write(df2[col].value_counts())


processing_time = time.time() - load_time
st.write(f"Datenverarbeitung dauerte: {processing_time:.4f} Sekunden")