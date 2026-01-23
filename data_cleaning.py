### Muss nur ausgeführt werden wenn das Dashboard ohne Datenbank ausgeführt werden soll

import pandas as pd
import numpy as np
import metrics as mt

def load_data():
    """This function loads the raw data from the programs 'resources' folder. Three .parquet files are expected: 'Auftragsdaten', 'Positionsdaten' and 'Auftragsdaten_Zeit'.

    Returns
    -------
    pandas.DataFrame
        Auftragsdaten
    pandas.DataFrame
        Positionsdaten
    pandas.DataFrame
        Auftragsdaten_Zeit
    """
    print("Loading Data...")
    df = pd.read_parquet("resources/Auftragsdaten")
    df2 = pd.read_parquet("resources/Positionsdaten")
    df3 = pd.read_parquet("resources/Auftragsdaten_Zeit")

    return df, df2, df3


def data_cleaning(df, df2, df3):
    """This function merges the given raw data sets with appropriate timestamp data and adds columns for more expedient metric computation. 

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing 'Auftragsdaten' data set
    df2 : pandas.DataFrame
        DataFrame containing 'Positionsdaten' data set_
    df3 : pandas.DataFrame
        DataFrame containing 'Auftragsdaten_Zeit' data set

    Returns
    -------
    pandas.DataFrame, pandas.DataFrame
       cleaned Auftrags- and Positionsdaten sets with timestamp information added
        
    Notes
    -----
    List of steps performed:
    - (extensive) timestamps added to df from df3, cleanup after merge
    - CRMEingangszeit timestamp added to df2, grouped by order
    - New column (int16) in df: number of positions for order
    - Replace custom null indicators with standard Null
    - Correction of common typing errors from data entry
    - Tyoe conversions and downcasting as appropriate for each column
    - New column (bool) in df2 with information on row correctly reflecting a discount position

    

    """
    print("Starting data cleaning...")
    #add timestamp columns to Auftragsdaten
    df = pd.merge(df, df3, on='KvaRechnung_ID', how='left') 
    # remove duplicate columns introduced by df3
    df = df.drop(["Auftrag_ID_y", "Schadensnummer_y"], axis=1) 
    #restore original column naming in df
    df = df.rename(columns={'Auftrag_ID_x': 'AuftragID', 'Schadensnummer_x': 'Schadensnummer'}) 
    #transfer timestamps for orders to associated position data
    df2 = pd.merge(df2,df[['KvaRechnung_ID','CRMEingangszeit']], on='KvaRechnung_ID', how='left')
   
    #add int column with number of positions for every entry in Auftragsdaten, downcast to save space
    df = pd.merge(df,mt.position_count(df2), on='KvaRechnung_ID', how='left')
    df['PositionsAnzahl'] = df['PositionsAnzahl'].astype('Int16')

    #checking effectivness of dtype changes, print initial state
    print(f"Memory usage before converting:")
    df.info(memory_usage='deep')
    df2.info(memory_usage='deep')

    #multiple columns contain custom indicators or empty fields, these are transformed into proper null values
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

    #checking effectivness of dtype changes, print 'after' state
    print(f"Memory usage after converting:")
    df.info(memory_usage='deep')
    df2.info(memory_usage='deep')


    # Add boolean column to check if row is a discount position
    keywords = ["Rabatt", "Skonto", "Nachlass", "Gutschrift", "Bonus", "Abzug", "Minderung", "Gutschein", "Erlass", "Storno", "Kulanz"]

    pattern = '|'.join(keywords)
    df2['ist_Abzug'] = df2['Bezeichnung'].str.contains(pattern, case=False, regex=True, na=False)
    normal_position = (df2['Einigung_Netto'] >= 0) & (df2['ist_Abzug'] == False)
    discount_position = (df2['Einigung_Netto'] < 0) & (df2['ist_Abzug'] == True)

    df2['Plausibel'] = normal_position | discount_position

    return df, df2


# Legacy: data_cleaning can be run as a standalone script if needed (if no duckdb is used, the dashboard expects modified data sets).
# Results are written to the 'resources' folder.
if __name__ == "__main__":
    auftragsdaten, positionsdaten, zeitdaten = load_data()
    df, df2 = data_cleaning(auftragsdaten, positionsdaten, zeitdaten)

    df.to_parquet("resources/Auftragsdaten_konvertiert")
    df2.to_parquet("resources/Positionsdaten_konvertiert")