import pandas as pd

df = pd.read_parquet("resources/Auftragsdaten_konvertiert")
#df2 = pd.read_parquet("resources/Positionsdaten_konvertiert")


def ratio_null_values(input_df):
    length_df = len(input_df)
    ratio_dict = {}
    for column in input_df.columns:
        null_values = input_df[column].isna().sum()
        ratio_null = round(null_values / length_df * 100, 2) # In Percent
        ratio_dict[column] = ratio_null
    
    return ratio_dict

def Kundengruppe_containing_test(df):
    anzahl_test = len(df[df['Kundengruppe'].str.contains('test', case=False, na=False)])
    #test_Kundengruppen = df[df['Kundengruppe'].str.contains('test', case=False, na=False)]
    return anzahl_test


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
    
    return count, avg

print(plausibilitaetscheck_forderung_einigung(df))
