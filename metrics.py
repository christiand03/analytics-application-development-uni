import pandas as pd
import numpy as np

print("Loading Data...")
df = pd.read_parquet("resources/Auftragsdaten_konvertiert")
#df2 = pd.read_parquet("resources/Positionsdaten_konvertiert")
print("Data loaded.")

# wird nur wiederverwendet
def ratio_null_values_column(input_df):
    length_df = len(input_df)
    ratio_dict = {}
    for column in input_df.columns:
        null_values = input_df[column].isna().sum()
        ratio_null = round(null_values / length_df * 100, 2) # In Percent
        ratio_dict[column] = ratio_null
    
    return ratio_dict

# wird nur wiederverwendet
def ratio_null_values_rows(input_df, relevant_columns=None):
    if relevant_columns is None:
        df_to_check = input_df
    else:
        df_to_check = input_df[relevant_columns]

    total_rows = len(df_to_check)
    if total_rows == 0:
        return 0.0

    null_rows = df_to_check.isnull().any(axis=1).sum()
    row_ratio = (null_rows / total_rows) * 100

    return row_ratio

# gibt die Anzahl und wahlweise auch den dataframe aus wo eine Test-Kundengruppe verwendet wurde
def Kundengruppe_containing_test(df):
    anzahl_test = len(df[df['Kundengruppe'].str.contains('test', case=False, na=False)])
    #test_Kundengruppen = df[df['Kundengruppe'].str.contains('test', case=False, na=False)]
    return anzahl_test

# Allgemeine Statistiken für numerische Spalten als dictionary, könnte als dataframe erweitert werden
def allgemeine_statistiken_num(input_df):
    statistiken = {}
    
    for num_col in input_df.select_dtypes('number').columns:
        statistiken[num_col] = {}
        mean = input_df[num_col].mean()
        median = input_df[num_col].median()
        std = input_df[num_col].std()
        min = input_df[num_col].min()
        max = input_df[num_col].max()

        statistiken[num_col]['mean'] = mean
        statistiken[num_col]['median'] = median
        statistiken[num_col]['std'] = std
        statistiken[num_col]['min'] = min
        statistiken[num_col]['max'] = max

    return statistiken

# checkt ob einigung > forderung; gibt liste der fehlerhaften Datensätze, die anzahl und die durchschnittliche Abweichung zurück 
def plausibilitaetscheck_forderung_einigung(input_df):
    statistik = []
    count = 0
    for index, row in input_df.iterrows():
        if round(row['Einigung_Netto'], 2) > round(row['Forderung_Netto'], 2):
            count += 1
            difference = round(row['Einigung_Netto'] - row['Forderung_Netto'],2)
            statistik.append(difference)
            #print(f"Forderung: {row['Forderung_Netto']:.2f}, Einigung: {row['Einigung_Netto']:.2f}")
    
    if count > 0:
        avg = sum(statistik) / len(statistik)
    else:
        avg = 0
    
    return statistik, count, avg

# Checkt ob die uniquen IDs auch wirklich unique sind
def uniqueness_check(df, df2):
    kvarechnung_id_is_unique = df['KvaRechnung_ID'].is_unique
    position_id_is_unique = df2['Position_ID'].is_unique
    
    return kvarechnung_id_is_unique, position_id_is_unique

# Metric to display number of rows after applying filters
def count_rows(input_df):
    count = len(input_df)
    return count

# deprecated
def split_dataframe(input_df, chunks=5):
    return np.array_split(input_df, chunks)

# row-/column-wise none ratio metric
def data_cleanliness(input_df):
    # needs to be set by Frontend
    group_by_col = "Kundengruppe"

    if group_by_col is None:
        null_ratio_rows = ratio_null_values_rows(input_df)
        null_ratio_cols = ratio_null_values_column(input_df)

        return null_ratio_rows, null_ratio_cols

    else:
        # Group for columns & rows
        grouped_null_counts = input_df.groupby(group_by_col).apply(lambda x: x.isnull().sum())
        grouped_null_rows = input_df.groupby(group_by_col).apply(lambda x: x.isnull().any(axis=1).sum())
        
        # create group sizes
        group_sizes = input_df.groupby(group_by_col).size()
        
        # calculate ratios
        grouped_col_ratios = grouped_null_counts.div(group_sizes, axis=0)
        grouped_row_ratios = grouped_null_rows / group_sizes

        return grouped_col_ratios, grouped_row_ratios

# to group by the selected column
def groupby_col(input_df, col):
    input_df_grouped = input_df.groupby(col)

    return input_df_grouped

# to check if a row is falsely positive or negative
def discount_check(df2):
    potential_errors = (~df2['Plausibel']).sum()
    return potential_errors

# give the dataframe of Proformabelege and the count
def proformabelege(df):
    proforma = df[df['Einigung_Netto'].between(0.01, 1)]
    proforma_count = len(proforma)
    return proforma, proforma_count

# das muss noch besser gemacht werden
def position_count(input_df):
    position_count = input_df.groupby('KvaRechnung_ID')['Position_ID'].count().reset_index()
    print(type(position_count))
    return position_count

# if everything is negative then its allowed, otherwise its false
def einigung_negativ(df):
    einigung_negative = df['Einigung_Netto'] < 0
    all_negative = (df['Forderung_Netto'] < 0) & (df['Empfehlung_Netto'] < 0)
    false_data = df[einigung_negative & ~all_negative]
    error_count = len(false_data)

    return error_count

# gives dataframe of all values above 50k
def above_50k(df):
    suspicious_data = df[df['Einigung_Netto'] >= 50000]
    return suspicious_data

# checks if Zeitwert is different to the difference of Forderung - Einigung
def check_zeitwert(df):
    zeitwert_error = [] # positive = not enough difference, negative = too much difference
    count = 0
    for index, row in df.iterrows():
        if round(row['Forderung_Netto'], 2) - round(row['Einigung_Netto'], 2) != round(row['Differenz_vor_Zeitwert_Netto'], 2):
            count += 1
            difference = round(row['Forderung_Netto'] - row['Einigung_Netto'], 2) - round(row['Differenz_vor_Zeitwert_Netto'], 2)
            zeitwert_error.append(difference)
    
    return zeitwert_error
            

length = len(check_zeitwert(df))
print(length)
