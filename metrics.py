import pandas as pd
import numpy as np

print("Loading Data...")
#df = pd.read_parquet("resources/Auftragsdaten_konvertiert")
df2 = pd.read_parquet("resources/Positionsdaten_konvertiert")
print("Data loaded.")

# wird nur wiederverwendet
def ratio_null_values_column(input_df):
    """Helper function that calculates the null-value-ratios for each column of the supplied DataFrame. 

    Parameters
    ----------
    input_df : pandas.DataFrame
        DataFrame that is to be evaluated.

    Returns
    -------
    ratio_dict: dict
        Dictionary of the form
          {column_name=  null_ratio (float)}
        with null_ratio being the percentage amount of null entries in the column  
    """    
    length_df = len(input_df)
    ratio_dict = {}
    for column in input_df.columns:
        null_values = input_df[column].isna().sum()
        ratio_null = round(null_values / length_df * 100, 2) # In Percent
        ratio_dict[column] = ratio_null
    
    return ratio_dict

# wird nur wiederverwendet
def ratio_null_values_rows(input_df, relevant_columns=None):
    """Helper function that calculates the ratio of rows containing null values in all / only chosen columns
       to total number of rows.  

    Parameters
    ----------
    input_df : pandas.DataFrame
        DataFrame that is to be evaluated.
    relevant_columns : list, optional
        List of column identifiers; function will only evaluate these columns, by default None.

    Returns
    -------
    row_ratio: float
        Percentage value of rows with at least one null value in the given columns.
    """    
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

def Kundengruppe_containing_test(df, return_frame=False):
    """Determines the number of rows in the 'Auftragsdaten' data set that are part of a test data set. 
       Optionally returns a data frame with all relevant instances.
       A row is conidered test data, if the entry in 'Kundengruppe' is named accordingly.

    Parameters
    ----------
    df : pandas.DataFrame
        'Auftragsdaten'-DataFrame that is to be evaluated.
    return_frame : bool, optional
        If True, this function returns a DataFrame with all found test data, by default False

    Returns
    -------
    anzahl_test: int
        total number of test data rows.
    test_Kundengruppen: pandas.DataFrame, optional
        DataFrame containing all found test data, returned only if return_frame = True
    """    
    test_Kundengruppen = df[df['Kundengruppe'].str.contains('test', case=False, na=False)]
    #anzahl_test = len(df[df['Kundengruppe'].str.contains('test', case=False, na=False)])
    anzahl_test = len(test_Kundengruppen)
    if return_frame:
        return anzahl_test, test_Kundengruppen 
    else:
        return anzahl_test

# Allgemeine Statistiken für numerische Spalten als dictionary, könnte als dataframe erweitert werden
def allgemeine_statistiken_num(input_df):
    """Calculates simple statistical values for all columns containing number data. 

    Parameters
    ----------
    input_df : pandas.DataFrame
        DataFrame that is to be evaluated.

    Returns
    -------
    statistiken: dict
        nested dictionary containing a dictionary for each column of input_df of the following form:
            {mean= float, 
            median= float,
            std= float,
            min= float,
            max= float}
        
    """
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
    """Checks for diff between Einigung_Netto and Forderung_Netto for all rows in the given dataframe.
       Einigung > Forderung is assumed as significant.

        Paramters
        ---------
        input_df: pandas.DataFrame
            DataFrame that is to be evaluated.
        
        Returns
        -------        
        statistik: list
            a list of all differences >0 as float values 
        count: int    
            total number of rows with difference >0 
        avg: float
            average difference over all found instances    
    """
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


def uniqueness_check(df, df2):
    """Checks whether the assumed unique ID columns in the data sets are truly unique.   

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame that contains the 'Auftragsdaten' data set
    df2 : pandas.DataFrame
        DataFrame that contains the 'Positionsdaten' data set

    Returns
    -------
    kvarechnung_id_is_unique: bool
        True if column is unique.
    position_id_is_unique : bool    
        True if column is unique.
    """
    kvarechnung_id_is_unique = df['KvaRechnung_ID'].is_unique
    position_id_is_unique = df2['Position_ID'].is_unique
    
    return kvarechnung_id_is_unique, position_id_is_unique


def count_rows(input_df):
    """Helper function to calculate the number of rows in a data frame after filtering.

    Parameters
    ----------
    input_df : pandas.DataFrame
        DataFrame to be evaluated.

    Returns
    -------
    count: int
        _description_
    """
    count = len(input_df)
    return count

 
# def split_dataframe(input_df, chunks=5):
#     """deprecated function, was supposed to simulate a time series in the data. Made obsolete by added date data. 
#     """
#     return np.array_split(input_df, chunks)


def data_cleanliness(input_df, group_by_col=None):
    """Determines ratio of null-values by columns and percentage of rows containing any amount of null values, 
       with optional grouping by a given column (currently dummied to Kundengruppe, remove once implemented in frontend).

    Parameters
    ----------
    input_df : pandas.DataFrame
        DataFrame that is to be evaluated.
    group_by_col: string, optional
        Column identifier for grouping

    Returns
    -------
    null_ratio_rows: float, optional
       Percentage value of rows with at least one null value in the given columns.
    null_ratio_cols: dict, optional
         Dictionary of the form
          {column_name=  null_ratio (float)}
         with null_ratio being the percentage amount of null entries in the column.   
    grouped_row_ratios: pandas.Series, optional
        Series containing the row ratios of all groups as float.
    grouped_col_ratios: pandas.DataFrame, optional 
        DataFrame containing groups and null-value-ratios per column for each.             
    """      
    group_by_col = "Kundengruppe" #TODO: needs to be set by Frontend, remove this once implemented in dashboard

    if group_by_col is None:
        null_ratio_rows = ratio_null_values_rows(input_df)
        null_ratio_cols = ratio_null_values_column(input_df)

        return null_ratio_rows, null_ratio_cols

    else:
        grouped = input_df.groupby(group_by_col)
        # Group for columns & rows
        grouped_null_counts = grouped.apply(lambda x: x.isnull().sum())
        grouped_null_rows = grouped.apply(lambda x: x.isnull().any(axis=1).sum())
        
        # create group sizes
        group_sizes = grouped.size()
        
        # calculate ratios
        grouped_col_ratios = grouped_null_counts.div(group_sizes, axis=0)
        grouped_row_ratios = grouped_null_rows / group_sizes

        return grouped_row_ratios, grouped_col_ratios


def groupby_col(input_df, col):
    """Helper function that groups a DataFrame by the given column.

    Parameters
    ----------
    input_df :  pandas.DataFrame
        DataFrame that is to be evaluated..
    col : string
        Identifier of the column to be grouped by.

    Returns
    -------
    input_df_grouped: pandas.DataFrame 
        A grouped DataFrame.
    """
    input_df_grouped = input_df.groupby(col)

    return input_df_grouped


def discount_check(df2):
    """Checks if a row in the 'Positionsdaten' data set does/doesn't describe a discount or similar and if the 'Einigung_Netto' and 'Forderung_Netto' information accurately reflects this (negative or positive).
       Whether this is the case relies on a check made in data_cleaning.py that writes its results to the 'Plausibel' column. 

    Parameters
    ----------
    df2 : pandas.DataFrame
        DataFrame containing the 'Positionsdaten' data set

    Returns
    -------
    potential_errors: int
        The number of potentially faulty rows
        
    """
    potential_errors = (~df2['Plausibel']).sum()
    return potential_errors

# give the dataframe of Proformabelege and the count
def proformabelege(df):
    """Function that checks for pro forma receipts in the 'Auftragsdaten' data set. 

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame that is to be evaluated.

    Returns
    -------
    proforma: pandas.DataFrame
        DataFrame containing all found pro forma receipt rows
    proforma_count: int
        Amount of found receipts    
    """
    proforma = df[df['Einigung_Netto'].between(0.01, 1)]
    proforma_count = len(proforma)
    return proforma, proforma_count

# das muss noch besser gemacht werden
# vllt als Spalte in Auftragsdaten_konvertiert? 
def position_count(input_df):
    """Counts the number of positions for each unique KvaRechnung_ID

    Parameters
    ----------
    input_df : input_df : pandas.DataFrame
        DataFrame that is to be evaluated.

    Returns
    -------
    position_count: pandas.DataFrame
        DataFrame with the columns 'KvaRechnung_ID' and the amount of associated positions.  
    """
    position_count = input_df.groupby('KvaRechnung_ID')['Position_ID'].count().reset_index()
    print(type(position_count))
    return position_count


def false_negative_df(df):
    """Function that checks if, when at least two values in the Tuple (Forderung, Empfehlung, Einigung) in the 'Auftragsdaten' data set are negative,
       the last remaining value is also negative. All instances where this doesnt hold are collected and counted.       

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with 'Auftragsdaten' data set that is to be evaluated.

    Returns
    -------
    error_count: int
        Number of entries in any of the three columns Forderung, Empfehlung or Einigung failing the check.
    """
    is_negative = {# Select all rows with negative entries in given column
        "Einigung_Netto": df['Einigung_Netto'] < 0,
        "Empfehlung_Netto": df["Empfehlung_Netto"] < 0,
        "Forderung_Netto": df["Forderung_Netto"] < 0, 
    }

    others_are_negative = {# Select all rows with both other columns being negative
        "Einigung_Netto": (df['Forderung_Netto'] < 0) & (df['Empfehlung_Netto'] < 0), 
        "Empfehlung_Netto": (df['Forderung_Netto'] < 0) & (df['Einigung_Netto'] < 0),
       "Forderung_Netto": (df['Einigung_Netto'] < 0) & (df['Empfehlung_Netto'] < 0),
    }

    false_negatives = {
        col: (is_negative[col] & ~others_are_negative[col])
        for col in is_negative
    }
    error_count = sum(bool_mask.sum() for bool_mask in false_negatives.values())
    return error_count

    # einigung_negative = df['Einigung_Netto'] < 0
    # else_negative = (df['Forderung_Netto'] < 0) & (df['Empfehlung_Netto'] < 0)
    # einigung_false_data = df[einigung_negative & ~else_negative]

    # empfehlung_negative = df['Empfehlung_Netto'] < 0
    # else_negative = (df['Forderung_Netto'] < 0) & (df['Einigung_Netto'] < 0)
    # empfehlung_false_data = df[empfehlung_negative & ~else_negative]

    # forderung_negative = df['Forderung_Netto'] < 0
    # else_negative = (df['Einigung_Netto'] < 0) & (df['Empfehlung_Netto'] < 0)
    # forderung_false_data = df[forderung_negative & ~else_negative]

    # error_count = len(einigung_false_data) + len(empfehlung_false_data) + len(forderung_false_data)
    # return error_count
 


# same for df2, total error count can contain multiple errors for the same row so total error count != row count with errors
def false_negative_df2(df2):
    """Checks Positionsdaten data set for entries in the columns 'Menge', 'Menge_Einigung', 'EP', 'Ep_Einigung',
       'Forderung_Netto' and 'Einigung_Netto' that are out of sensible value range. Returns the total error count over all columns. 

    Parameters
    ----------
    df2 : pandas.DataFrame
        DataFrame containing 'Positionsdaten' data set that is to be evaluated.

    Returns
    -------
    total_errors: int
        Total amount of non-valid entries aggregated over all relevant columns. 
    """
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
    """Checks for all receipts or positions that exceed a limit for suspicion of €50k in Einigung_Netto and need to be manually vetted.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame that is to be evaluated.

    Returns
    -------
    suspicious_data: pandas.DataFrame
        Data frame containing suspiciously high positions
    """
    suspicious_data = df[df['Einigung_Netto'] >= 50000]
    return suspicious_data


def check_zeitwert(df):
    """Checks if the value in the column 'Differenz_vor_Zeitwert_Netto' satisfies the condition [Zeitwert = Forderung-Einigung]
       and calculates the relative error. Only valid for 'Auftragsdaten' data set.     

    Parameters
    ----------
    df : _pandas.DataFrame
        DataFrame containing 'Auftragsdaten' data set that is to be evaluated.
    Returns
    -------
    zeitwert_error: list
        List of all error values (float) found in the data frame
    """
    zeitwert_error = [] # positive = not enough difference, negative = too much difference
    count = 0
    for index, row in df.iterrows():
        difference = round(row['Forderung_Netto'] - row['Einigung_Netto'], 2) - round(row['Differenz_vor_Zeitwert_Netto'], 2)
        if difference != 0:
            count += 1
            zeitwert_error.append(difference)
    
    return zeitwert_error
            

#print(false_negative_df2(df2))

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
