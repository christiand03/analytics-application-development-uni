import streamlit as st
import pandas as pd

st.set_page_config(page_title="Doppelte KvaRechnung_Nummern", layout="wide")
st.title("🔁 Alle doppelten KvaRechnung_Nummern (inkl. Redundanz)")

# Parquet-Datei laden
try:
    df = pd.read_parquet("resources/Auftragsdaten_konvertiert")
except Exception as e:
    st.error(f"Fehler beim Laden der Datei: {e}")
    st.stop()

# Prüfen, ob Spalte existiert
if 'KvaRechnung_Nummer' not in df.columns:
    st.error("Spalte 'KvaRechnung_Nummer' existiert nicht im DataFrame!")
    st.stop()

# Nur nicht-leere Werte berücksichtigen
df_clean = df.dropna(subset=['KvaRechnung_Nummer']).copy()
df_clean['KvaRechnung_Nummer'] = df_clean['KvaRechnung_Nummer'].astype(str)

# Alle doppelten Zeilen (inkl. Redundanz) finden
duplicates_all = df_clean[df_clean.duplicated(subset=['KvaRechnung_Nummer'], keep=False)]

st.subheader(f"➡️ Es gibt {len(duplicates_all)} doppelte Einträge (inkl. Redundanz)")

if not duplicates_all.empty:
    # Tabelle anzeigen
    st.dataframe(duplicates_all, use_container_width=True)
else:
    st.success("✅ Keine doppelten Werte gefunden!")








"""
import pandas as pd
df = pd.read_parquet("resources/Auftragsdaten_konvertiert")

# Prüfen, ob Spalte existiert
if 'KvaRechnung_Nummer' not in df.columns:
    raise KeyError("Spalte 'KvaRechnung_Nummer' existiert nicht im DataFrame!")

# Entferne NaN-Werte (falls vorhanden)
kva = df['KvaRechnung_Nummer']


# 2️⃣ Beginn mit 'KVR-' prüfen
starts_with_kvr = kva.str.startswith("KVR-")
print(f"Alle beginnen mit 'KVR-': {starts_with_kvr.all()}")
if not starts_with_kvr.all():
    print("➡️ Diese Werte beginnen NICHT mit 'KVR-':")
    print(kva[~starts_with_kvr].head())

# 3️⃣ Eindeutigkeit prüfen
is_unique = kva.is_unique
print(f"Alle Werte sind eindeutig: {is_unique}")
if not is_unique:
    duplicates = kva[kva.duplicated(keep=False)]
    print("➡️ Doppelte Werte:")
    print(duplicates)

"""
"""
df2 = pd.read_parquet("resources/Positionsdaten_konvertiert")

# Prüfen, ob Spalte existiert
if 'KvaRechnung_Nummer' not in df2.columns:
    raise KeyError("Spalte 'KvaRechnung_Nummer' existiert nicht im DataFrame!")

# Entferne NaN-Werte (falls vorhanden)
kva = df2['KvaRechnung_Nummer']


# 2️⃣ Beginn mit 'KVR-' prüfen
starts_with_kvr = kva.str.startswith("KVR-")
print(f"Alle beginnen mit 'KVR-': {starts_with_kvr.all()}")
if not starts_with_kvr.all():
    print("➡️ Diese Werte beginnen NICHT mit 'KVR-':")
    print(kva[~starts_with_kvr].head())

# 3️⃣ Eindeutigkeit prüfen
is_unique = kva.is_unique
print(f"Alle Werte sind eindeutig: {is_unique}")
if not is_unique:
    duplicates = kva[kva.duplicated(keep=False)]
    print("➡️ Doppelte Werte:")
    print(duplicates)
"""