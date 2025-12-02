import pandas as pd
import numpy as np

print("Loading Data...")
#df = pd.read_parquet("resources/Auftragsdaten_konvertiert")
df2 = pd.read_parquet("resources/Positionsdaten_konvertiert")
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
def false_negative_df(df):
    einigung_negative = df['Einigung_Netto'] < 0
    else_negative = (df['Forderung_Netto'] < 0) & (df['Empfehlung_Netto'] < 0)
    einigung_false_data = df[einigung_negative & ~else_negative]

    empfehlung_negative = df['Empfehlung_Netto'] < 0
    else_negative = (df['Forderung_Netto'] < 0) & (df['Einigung_Netto'] < 0)
    empfehlung_false_data = df[empfehlung_negative & ~else_negative]

    forderung_negative = df['Forderung_Netto'] < 0
    else_negative = (df['Einigung_Netto'] < 0) & (df['Empfehlung_Netto'] < 0)
    forderung_false_data = df[forderung_negative & ~else_negative]

    error_count = len(einigung_false_data) + len(empfehlung_false_data) + len(forderung_false_data)
    return error_count

# same for df2, total error count can contain multiple errors for the same row so total error count != row count with errors
def false_negative_df2(df2):
    count_menge_neg = (df2['Menge'] < 0).sum()
    count_menge_einigung_neg = (df2['Menge_Einigung'] < 0).sum()

    error_ep = ((df2['EP'] < 0) & (df2['EP_Einigung'] >= 0)).sum()
    error_ep_einigung = ((df2['EP_Einigung'] < 0) & (df2['EP'] >= 0)).sum()

    error_forderung = ((df2['Forderung_Netto'] < 0) & (df2['Einigung_Netto'] >= 0)).sum()
    error_einigung = ((df2['Einigung_Netto'] < 0) & (df2['Forderung_Netto'] >= 0)).sum()

    total_errors = (count_menge_neg + count_menge_einigung_neg + error_ep + error_ep_einigung + error_forderung + error_einigung)
    return total_errors

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
            

print(false_negative_df2(df2))

def positions_per_order_over_time(df, df2, time_col="CRMEingangszeit"):
    """
    Berechnet die durchschnittliche Anzahl an Positionen pro Auftrag je Monat.

    Args:
        df: Auftragsdaten mit Spalte 'KvaRechnung_ID' und einer Zeitspalte.
        df2: Positionsdaten mit Spalten 'KvaRechnung_ID' und 'Position_ID'.
        time_col: Name der Zeitspalte in orders_df (z.B. 'CRMEingangszeit').

    Returns:
        DataFrame mit Spalten:
        - 'Zeitperiode'
        - 'Avg_Positionen_pro_Auftrag'
        - 'Total_Positionen'
        - 'Anzahl_Auftraege'
        - 'Growth_rate_%'
    """

    # Positionen pro Auftrag zählen
    pos_counts = (
        df2
        .groupby("KvaRechnung_ID")["Position_ID"]
        .count()
        .reset_index(name="Positionen_pro_Auftrag")
    )

    # Zeitspalte vorbereiten
    orders = df[["KvaRechnung_ID", time_col]].copy()
    orders = orders.dropna(subset=[time_col])
    orders[time_col] = pd.to_datetime(orders[time_col], errors="coerce")
    orders = orders.dropna(subset=[time_col])

    # Zeitperiode (Monat) bestimmen
    orders["Zeitperiode"] = orders[time_col].dt.to_period("M").astype(str)

    # Positionen an Aufträge mergen
    merged = orders.merge(pos_counts, on="KvaRechnung_ID", how="left")
    merged["Positionen_pro_Auftrag"] = merged["Positionen_pro_Auftrag"].fillna(0)

    # Aggregation je Zeitperiode
    result = (
        merged
        .groupby("Zeitperiode")["Positionen_pro_Auftrag"]
        .agg(["mean", "sum", "count"])
        .reset_index()
    )

    result = result.sort_values("Zeitperiode")

    result = result.rename(
        columns={
            "mean": "Avg_Positionen_pro_Auftrag",
            "sum": "Total_Positionen",
            "count": "Anzahl_Auftraege"
        }
    )

    # prozentuale Veränderung der durchschnittlichen Positionsanzahl
    result["Growth_rate_%"] = result["Avg_Positionen_pro_Auftrag"].pct_change() * 100

    return result

def error_frequency_by_weekday_hour(df, time_col="CRMEingangszeit", relevant_columns=None):
    """
    Aggregiert die Fehlerhäufigkeit (NaN-Werte) nach Wochentag und Stunde.

    Error-Definition:
        Ein Auftrag gilt als fehlerhaft, wenn in mindestens einer der relevanten Spalten
        ein NaN-Wert vorkommt.

    Args:
        df: Auftragsdaten-DataFrame (z.B. Auftragsdaten_konvertiert),
            muss 'KvaRechnung_ID' und die Zeitspalte enthalten.
        time_col: Name der Zeitspalte in df, z.B. 'CRMEingangszeit'.
        relevant_columns: Liste der Spalten, die auf NaN geprüft werden sollen.
                          Wenn None -> alle Spalten außer 'KvaRechnung_ID' und time_col.

    Returns:
        DataFrame mit Spalten:
        - 'weekday'     : Name des Wochentags (Monday, Tuesday, ...)
        - 'hour'        : Stunde (0–23)
        - 'total_rows'  : Anzahl Aufträge in diesem Zeit-Slot
        - 'error_rows'  : Anzahl fehlerhafter Aufträge in diesem Slot
        - 'error_rate'  : Fehlerquote in Prozent
    """

    work_df = df.copy()

    # Zeitspalte in datetime umwandeln
    work_df[time_col] = pd.to_datetime(work_df[time_col], errors="coerce")
    work_df = work_df.dropna(subset=[time_col])

    # Wochentag + Stunde extrahieren
    work_df["weekday"] = work_df[time_col].dt.day_name()
    work_df["hour"] = work_df[time_col].dt.hour

    # Relevante Spalten bestimmen
    if relevant_columns is None:
        exclude = {time_col, "KvaRechnung_ID", "weekday", "hour"}
        relevant_columns = [c for c in work_df.columns if c not in exclude]

    if not relevant_columns:
        raise ValueError("Keine relevanten Spalten für die Fehlerprüfung gefunden.")

    # Error = mind. ein NaN in den relevanten Spalten
    work_df["has_error"] = work_df[relevant_columns].isna().any(axis=1)

    result = (
        work_df
        .groupby(["weekday", "hour"])
        .agg(
            total_rows=("KvaRechnung_ID", "count"),
            error_rows=("has_error", "sum"),
        )
        .reset_index()
    )

    result["error_rate"] = result["error_rows"] / result["total_rows"] * 100

    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    result["weekday"] = pd.Categorical(result["weekday"], categories=weekday_order, ordered=True)
    result = result.sort_values(["weekday", "hour"])

    return result
