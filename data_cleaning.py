import pandas as pd
import numpy as np
import metrics as mt

print("Loading Data...")
df = pd.read_parquet("resources/Auftragsdaten")
df2 = pd.read_parquet("resources/Positionsdaten")
df3 = pd.read_parquet("resources/Auftragsdaten_Zeit")

df = pd.merge(df, df3, on='KvaRechnung_ID', how='left')
df = df.drop(["Auftrag_ID_y", "Schadensnummer_y"], axis=1)
df = df.rename(columns={'Auftrag_ID_x': 'AuftragID', 'Schadensnummer_x': 'Schadensnummer'})

#add int column with number of positions for every entry in Auftragsdaten
df = pd.merge(df,mt.position_count(df2), on='KvaRechnung_ID', how='left')

#checking effectivness of dtype changes, before state
print(f"Memory usage before converting:")
df.info(memory_usage='deep')
df2.info(memory_usage='deep')


None_placeholder = ["-", "(leer)", "(null)", "wird vergeben", "unbekannter HW", "#unbekannter hw", "Allgemeine Standardbeschreibungen"]
for placeholder in None_placeholder:
    df = df.replace(placeholder, pd.NA)
    df2 = df2.replace(placeholder, pd.NA)

# Replace Typing Error in Schadensart_Name
df = df.replace("Betriebsunterbrechnung", "Betriebsunterbrechung")

# Replace Typing Error in Falltyp_Name
df = df.replace("Überpannung Heizung", "Überspannung Heizung")
df = df.replace("Kfz", "KFZ")
df = df.replace("Schliessanlagen", "Schließanlagen")

# Converting Object Types for df
columns_to_convert = ['Land', 'PLZ_SO', 'PLZ_HW', 'PLZ_VN', 'address1_postalcode', 
                       'Schadenart_Name', 'Falltyp_Name', 'Gewerk_Name', 'Kundengruppe', 
                       'Handwerker_Name']

# Convert Column with low Cardinality to Category
df[columns_to_convert] = df[columns_to_convert].astype('category')

# Convert the other Object Columns to String
object_columns = df.select_dtypes('object').columns
df[object_columns] = df[object_columns].astype('string')


# Downcast integer columns
int_cols = df.select_dtypes(include=['int64']).columns
for col in int_cols:
    df[col] = pd.to_numeric(df[col], downcast='integer')

# Downcast float columns
df_below_four_decimals = df.select_dtypes(include='float') \
                                    .apply(lambda col: np.isclose(col, col.round(4))) \
                                    .any() \
                                    .loc[lambda s: s] \
                                    .index.tolist()

df[df_below_four_decimals] = df[df_below_four_decimals].astype('float32')

# Converting Object Types for df2
df2_columns_to_convert = ['KvaRechnung_ID', 'KvaRechnung_Nummer', 'Mengeneinheit', 'Bemerkung']

# Converting to Category
df2[df2_columns_to_convert] = df2[df2_columns_to_convert].astype('category')

# Converting the rest to strings
object_columns = df2.select_dtypes('object').columns
df2[object_columns] = df2[object_columns].astype('string')

# Downcast float columns
df2_below_four_decimals = df2.select_dtypes(include='float') \
                                    .apply(lambda col: np.isclose(col, col.round(4))) \
                                    .any() \
                                    .loc[lambda s: s] \
                                    .index.tolist()

df2[df2_below_four_decimals] = df2[df2_below_four_decimals].astype('float32')

print(f"Memory usage after converting:")
df.info(memory_usage='deep')
df2.info(memory_usage='deep')


# Add boolean column to check for discount
keywords = ["Rabatt", "Skonto", "Nachlass", "Gutschrift", "Bonus", "Abzug", "Minderung", "Gutschein", "Erlass", "Storno", "Kulanz"]

pattern = '|'.join(keywords)
df2['ist_Abzug'] = df2['Bezeichnung'].str.contains(pattern, case=False, regex=True, na=False)
#hier ist der Fall von Einigung_Netto = 0 bei Verwendung von manuellem Betrag nicht berücksichtigt, automatisch nicht plausibel
normal_position = (df2['Einigung_Netto'] > 0) & (df2['ist_Abzug'] == False)
discount_position = (df2['Einigung_Netto'] < 0) & (df2['ist_Abzug'] == True)

df2['Plausibel'] = normal_position | discount_position




df.to_parquet("resources/Auftragsdaten_konvertiert")
df2.to_parquet("resources/Positionsdaten_konvertiert")