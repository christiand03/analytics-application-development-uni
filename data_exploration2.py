import pandas as pd

#df = pd.read_parquet("resources/Auftragsdaten_konvertiert")
df2 = pd.read_parquet("resources/Positionsdaten_konvertiert")

#df_auftragsid = df['Auftrag_ID']

#print(df_auftragsid)
"""
for row in df_auftragsid:
    if len(row) > 36 or len(row) < 36:
        print(row)

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

df_kvarechnungid = df['KvaRechnung_ID']

for row in df_auftragsid:
    if len(row) > 36 or len(row) < 36:
        print(row)

for col in df_auftragsid_tupel.columns:
    print(f"--- Value Count für Spalte: '{col}' ---")
    print(df_auftragsid_tupel[col].value_counts())





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

for col in df_kvarechnungid_tupel.columns:
    print(f"--- Value Count für Spalte: '{col}' ---")
    print(df_kvarechnungid_tupel[col].value_counts())
"""


df2_kvarechnungid = df2['KvaRechnung_ID']