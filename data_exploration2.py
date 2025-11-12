import pandas as pd

df = pd.read_parquet("resources/Auftragsdaten_konvertiert")
df2 = pd.read_parquet("resources/Positionsdaten_konvertiert")

print("Starte mit Auftragsdaten/Auftrag_ID")
df_auftragsid = df['Auftrag_ID']

for row in df_auftragsid:
    if len(row) > 36 or len(row) < 36:
        print(row)
print("Auftragsdaten/Auftrag_ID Längenüberprüfung beendet.")

df_auftragsid_tupel = df_auftragsid.str.split('-', expand=True)
print(df_auftragsid_tupel)

for row in df_auftragsid_tupel[0]:
    if len(row) > 8 or len(row) < 8:
        print(row)

for row in df_auftragsid_tupel[1]:
    if len(row) > 4 or len(row) < 4:
        print(row)
    
for row in df_auftragsid_tupel[2]:
    if len(row) > 4 or len(row) < 4:
        print(row)

for row in df_auftragsid_tupel[3]:
    if len(row) > 4 or len(row) < 4:
        print(row)

for row in df_auftragsid_tupel[4]:
    if len(row) > 12 or len(row) < 12:
        print(row)

print("Auftrag_ID Tupel Längenüberprüfung beendet.")

for col in df_auftragsid_tupel.columns:
    print(f"--- Value Count für Spalte: '{col}' ---")
    print(df_auftragsid_tupel[col].value_counts())


print("Starte mit Auftragsdaten/KvaRechnung_ID")
df_kvarechnungid = df['KvaRechnung_ID']

for row in df_kvarechnungid:
    if len(row) > 36 or len(row) < 36:
        print(row)

print("Auftragsdaten/KvaRechnung_ID Längenüberprüfung beendet.")

df_kvarechnungid_tupel = df_kvarechnungid.str.split('-', expand=True)
print(df_kvarechnungid_tupel)

for row in df_kvarechnungid_tupel[0]:
    if len(row) > 8 or len(row) < 8:
        print(row)

for row in df_kvarechnungid_tupel[1]:
    if len(row) > 4 or len(row) < 4:
        print(row)
    
for row in df_kvarechnungid_tupel[2]:
    if len(row) > 4 or len(row) < 4:
        print(row)

for row in df_kvarechnungid_tupel[3]:
    if len(row) > 4 or len(row) < 4:
        print(row)

for row in df_kvarechnungid_tupel[4]:
    if len(row) > 12 or len(row) < 12:
        print(row)

print("KvaRechnung_ID Tupel Längenüberprüfung beendet.")

for col in df_kvarechnungid_tupel.columns:
    print(f"--- Value Count für Spalte: '{col}' ---")
    print(df_kvarechnungid_tupel[col].value_counts())


print("Starte mit Positionsdaten/KvaRechnung_ID")
df2_kvarechnungid = df2['KvaRechnung_ID']

for row in df2_kvarechnungid:
    if len(row) > 36 or len(row) < 36:
        print(row)

print("Positionsdaten/KvaRechnung_ID Längenüberprüfung beendet.")

df2_kvarechnungid_tupel = df2_kvarechnungid.str.split('-', expand=True)
print(df2_kvarechnungid_tupel)

for row in df2_kvarechnungid_tupel[0]:
    if len(row) > 8 or len(row) < 8:
        print(row)

for row in df2_kvarechnungid_tupel[1]:
    if len(row) > 4 or len(row) < 4:
        print(row)
    
for row in df2_kvarechnungid_tupel[2]:
    if len(row) > 4 or len(row) < 4:
        print(row)

for row in df2_kvarechnungid_tupel[3]:
    if len(row) > 4 or len(row) < 4:
        print(row)

for row in df2_kvarechnungid_tupel[4]:
    if len(row) > 12 or len(row) < 12:
        print(row)

print("KvaRechnung_ID Tupel Längenüberprüfung beendet.")

for col in df2_kvarechnungid_tupel.columns:
    print(f"--- Value Count für Spalte: '{col}' ---")
    print(df2_kvarechnungid_tupel[col].value_counts())


print("Starte mit Positionsdaten/Position_ID")
df2_positionid = df2['Position_ID']

for row in df2_positionid:
    if len(row) > 36 or len(row) < 36:
        print(row)
print("Positionsdaten/Position_ID Längenüberprüfung beendet.")

df2_positionid_tupel = df2_positionid.str.split('-', expand=True)
print(df2_positionid_tupel)

for row in df2_positionid_tupel[0]:
    if len(row) > 8 or len(row) < 8:
        print(row)

for row in df2_positionid_tupel[1]:
    if len(row) > 4 or len(row) < 4:
        print(row)
    
for row in df2_positionid_tupel[2]:
    if len(row) > 4 or len(row) < 4:
        print(row)

for row in df2_positionid_tupel[3]:
    if len(row) > 4 or len(row) < 4:
        print(row)

for row in df2_positionid_tupel[4]:
    if len(row) > 12 or len(row) < 12:
        print(row)
print("Position_ID Tupel Längenüberprüfung beendet.")

for col in df2_positionid_tupel.columns:
    print(f"--- Value Count für Spalte: '{col}' ---")
    print(df2_positionid_tupel[col].value_counts())
