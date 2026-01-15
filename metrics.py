import pandas as pd
import numpy as np
import re
import time
from sentence_transformers import SentenceTransformer
import torch

def load_data():
    df = pd.read_parquet("resources/Auftragsdaten_konvertiert")
    df2 = pd.read_parquet("resources/Positionsdaten_konvertiert")
    return df, df2

# wird nur wiederverwendet
def ratio_null_values_column(input_df):
    """Helper function that calculates the null-value-ratios for each column of the supplied DataFrame. 

    Parameters
    ----------
    input_df : pandas.DataFrame
        DataFrame that is to be evaluated.

    Returns
    -------
    ratio_dict: pd.DataFrame
        DataFrame of the form
          |column_name |  null_ratio (float)|
        with null_ratio being the percentage amount of null entries in the column  
    """
    null_ratio_df = pd.DataFrame(input_df.isna()
                             .mean()
                             .mul(100)
                             .round(2)
                             .rename("null_ratio")
                             .reset_index()
                             )
    return null_ratio_df

# wird nur wiederverwendet
def ratio_null_values_rows(input_df, exclude_cols=None):
    """Helper function that calculates the ratio of rows containing null values in all / only chosen columns to total number of rows.  
    
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
    if exclude_cols is None:
        exclude_cols = []
    
    df_to_check = input_df.drop(columns=exclude_cols, errors='ignore')

    total_rows = len(df_to_check)
    if total_rows == 0:
        return 0.0

    null_rows = df_to_check.isnull().any(axis=1).sum()
    row_ratio = (null_rows / total_rows) * 100

    return row_ratio

def Kundengruppe_containing_test(df, return_frame=False):
    """Determines the number of rows in the 'Auftragsdaten' data set that are part of a test data set. Optionally returns a data frame with all relevant instances. A row is conidered test data, if the entry in 'Kundengruppe' is named accordingly.

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
    test_Kundengruppen: pandas.DataFrame or None
        DataFrame containing all found test data, returned only if return_frame = True
    """
    test_Kundengruppen = df[df['Kundengruppe'].str.contains('test', case=False, na=False)]
    anzahl_test = len(test_Kundengruppen)
    if return_frame:
        return test_Kundengruppen
    else:
        return anzahl_test

# Allgemeine Statistiken für numerische Spalten als dictionary, könnte als dataframe erweitert werden, ### wird nicht mehr verwendet
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
    """Checks for diff between Einigung_Netto and Forderung_Netto for all rows in the given dataframe. Einigung > Forderung is assumed as significant error.

        Paramters
        ---------
        input_df: pandas.DataFrame
            DataFrame that is to be evaluated.
        
        Returns
        -------        
        results: pandas.DataFrame
            a DataFrame of all differences > 0 as float values alongside their ID and Forderung_Netto and Einigung_Netto 
        count: int  
            total number of rows with difference >0
        avg: float
            average difference over all found instances    
    """
    if 'AuftragID' in input_df.columns:
        cols = ["KvaRechnung_ID", "Forderung_Netto", "Einigung_Netto"]
    else:
        cols = ["Position_ID", "Forderung_Netto", "Einigung_Netto"]

    results = input_df[cols]
    faulty_rows_mask = results['Einigung_Netto'].round(2) > results['Forderung_Netto'].round(2)
    #count amount of positives
    count = faulty_rows_mask.sum()

    results['Diff'] = (results.loc[faulty_rows_mask, 'Einigung_Netto']-results.loc[faulty_rows_mask,'Forderung_Netto']).round(2)
    results = results[results['Diff'] > 0]
    avg = results['Diff'].mean()

    return results, count, avg


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


def split_dataframe(input_df, chunks=5):
    """ Splits the data frame to simulate a time series data.
        
        .. deprecated::  Made obsolete by added datetime columns. 
    """
    return np.array_split(input_df, chunks)


def data_cleanliness(input_df,group_by_col="Kundengruppe", specific_group=None):
    """Determines ratio of null-values by columns and percentage of rows containing any amount of null values, with optional grouping by a given column.

    Parameters
    ----------
    input_df : pandas.DataFrame
        DataFrame that is to be evaluated.
    group_by_col: string, optional
        Column identifier for grouping
    specific_group: string, optional
        Passes a group entry to filter the result by, if any   

    Returns
    -------
    null_ratio_rows: float or None
        Percentage value of rows with at least one null value in the given columns.
    null_ratio_cols: DataFrame or None
        DataFrame, with null_ratio being the percentage amount of null entries in the column.   
    grouped_row_ratios: pandas.Series or None
        Series containing the row ratios of all groups as float.
    grouped_col_ratios: pandas.DataFrame or None
        DataFrame containing groups and null-value-ratios per column for each.             
    """

    if group_by_col is None:
        if 'PLZ_SO' in input_df.columns:
            null_ratio_rows = ratio_null_values_rows(input_df, exclude_cols=['PLZ_SO', 'PLZ_HW', 'PLZ_VN', 'address1_postalcode'])
            null_ratio_cols = ratio_null_values_column(input_df)
            
        else:
            null_ratio_rows = ratio_null_values_rows(input_df, exclude_cols=['Bemerkung'])
            null_ratio_cols = ratio_null_values_column(input_df)

        return null_ratio_rows, null_ratio_cols

    else:

        grouped = input_df.groupby(group_by_col,observed=True)

        # Group for columns & rows
        grouped_null_counts = grouped.apply(lambda x: x.isnull().sum(), include_groups=False)
        grouped_null_rows = grouped.apply(lambda x: x.isnull().any(axis=1).sum(), include_groups=False)

        # create group sizes
        group_sizes = grouped.size()

        # calculate ratios
        grouped_col_ratios = grouped_null_counts.div(group_sizes, axis=0)
        grouped_row_ratios = grouped_null_rows / group_sizes
        if specific_group:
            grouped_col_ratios = grouped_col_ratios.loc[[specific_group]]
            grouped_row_ratios = grouped_row_ratios.loc[[specific_group]]
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
    input_df_grouped = input_df.groupby(col,observed=True)

    return input_df_grouped


def discount_check(df2):
    """Checks if a row in the 'Positionsdaten' data set does/doesn't describe a discount or similar and if the 'Einigung_Netto' and 'Forderung_Netto' information accurately reflects this (negative or positive values). 
    
    Parameters
    ----------
    df2 : pandas.DataFrame
        DataFrame containing the 'Positionsdaten' data set

    Returns
    -------
    potential_errors: int
        The number of potentially faulty rows

    Notes
    -----        
    This check relies on logic in data_cleaning.py that writes its results to the 'Plausibel' column. 
    
    """
    potential_errors = (~df2['Plausibel']).sum()
    return potential_errors


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
    position_count = input_df.groupby('KvaRechnung_ID', observed=False)['Position_ID'].count().reset_index().rename(columns={'Position_ID': 'PositionsAnzahl'})
    return position_count

def empty_orders(df):
    """Function that checks if any orders do not have positions associated with them.

    Parameters
    ----------
    df : pandas.DataFrame
         DataFrame with 'Auftragsdaten' data set that is to be evaluated.

    Returns
    -------
    empty_orders: int
          Total amount of orders that do not have any positions associated with them.
    """
    empty_orders = df['PositionsAnzahl'].isna().sum()
    return empty_orders



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




def false_negative_df2(df2):
    """Checks 'Positionsdaten' data set for entries in the columns 'Menge', 'Menge_Einigung', 'EP', 'Ep_Einigung',
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
    suspicious_data = suspicious_data[['KvaRechnung_ID', 'Forderung_Netto', 'Empfehlung_Netto', 'Einigung_Netto', 'Kundengruppe', 'Handwerker_Name', 'CRMEingangszeit']]
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
    result_df: pandas.DataFrame
        DataFrame of all error values (float) alongside the ID found in the original data frame
    """

    difference = (df['Forderung_Netto'] - df['Einigung_Netto']).round(2) - (df['Differenz_vor_Zeitwert_Netto']).round(2)
    mask = ~np.isclose(difference, 0, atol=0.01) # positive = not enough difference, negative = too much difference

    result_df = df.loc[mask, ['KvaRechnung_ID', 'CRMEingangszeit']].copy()
    result_df['Differenz Zeitwert'] = difference[mask]
    
    return result_df



# sollte auf jeden fall positions_count() nutzen
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
        .groupby("KvaRechnung_ID",observed=True)["Position_ID"]
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
        .groupby("Zeitperiode",observed=True)["Positionen_pro_Auftrag"]
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
    Aggregiert die Fehlerhäufigkeit (NaN-Werte) nach Wochentag und Stunde. Ein Auftrag gilt als fehlerhaft, wenn in mindestens einer der relevanten Spalten ein NaN-Wert vorkommt.

    Parameters
    ----------
        df: pandas.DataFrame
            Auftragsdaten-DataFrame (z.B. Auftragsdaten_konvertiert),muss 'KvaRechnung_ID' und die Zeitspalte enthalten.
        time_col: string
            Name der Zeitspalte in df, z.B. 'CRMEingangszeit'.
        relevant_columns: list
            Liste der Spalten, die auf NaN geprüft werden sollen.
            Wenn None -> alle Spalten außer 'KvaRechnung_ID' und time_col.

    Returns
    -------
        result: pandas.DataFrame
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
        .groupby(["weekday", "hour"],observed=True)
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


def get_mismatched_entries(df, threshold=0.2, process_batch_size=16384, encode_batch_size=128):
    """
    Calculates the semantic similarity between 'Gewerk_Name' and 'Handwerker_Name' using a 
    Sentence Transformer model on the GPU. Identifies entries where the similarity score 
    falls below the threshold.(< 0.2).
    
    Parameters:
    ----------
        df: pandas.DataFrame
            DataFrame (Auftragsdaten) that contains the columns 'Gewerk_Name' and 'Handwerker_Name'.
        threshold: float, optional
            Similarity threshold (default: 0.2). Values below this limit are considered mismatches.
            The optimal threshold in a production system would need to be evaluated further. 
        process_batch_size: int, optional
            Number of rows to be compared simultaneously (high value possible, e.g. 16384).
        encode_batch_size: int, optional
            Number of unique terms to be vectorized simultaneously by the model (low value recommended, e.g. 128).

    Returns:
    -------
        mismatches: pandas.DataFrame
            DataFrame containing rows where 'Similarity_Score' < threshold.
            The results are sorted ascending by similarity and include the new column 'Similarity_Score'.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Running on: {device}")
    
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device=device)

    df = df.dropna(subset=['Gewerk_Name', 'Handwerker_Name'])
    gewerk_codes, unique_gewerke = pd.factorize(df['Gewerk_Name'])
    handwerker_codes, unique_handwerker = pd.factorize(df['Handwerker_Name'])


    print("Encoding unique values...")
    emb_gewerke = model.encode(
        unique_gewerke, 
        batch_size=encode_batch_size, 
        show_progress_bar=True, 
        convert_to_tensor=True, 
        device=device,
        normalize_embeddings=True
    )

    emb_handwerker = model.encode(
        unique_handwerker, 
        batch_size=encode_batch_size, 
        show_progress_bar=True, 
        convert_to_tensor=True, 
        device=device,
        normalize_embeddings=True
    )


    print("Calculating similarity scores on GPU...")
    similarity_scores = []
    
    total_rows = len(df)
    
    t_gewerk_codes = torch.tensor(gewerk_codes, device=device, dtype=torch.long)
    t_handwerker_codes = torch.tensor(handwerker_codes, device=device, dtype=torch.long)

    with torch.no_grad():
        for i in range(0, total_rows, process_batch_size):
            end = min(i + process_batch_size, total_rows)
            
            batch_g_codes = t_gewerk_codes[i:end]
            batch_h_codes = t_handwerker_codes[i:end]
            
            batch_emb_g = emb_gewerke[batch_g_codes]
            batch_emb_h = emb_handwerker[batch_h_codes]
            
            sim = torch.nn.functional.cosine_similarity(batch_emb_g, batch_emb_h, dim=1)
            
            similarity_scores.append(sim.cpu().numpy())

    full_scores = np.concatenate(similarity_scores)
    df['Similarity_Score'] = full_scores
    
    mismatches = df[df['Similarity_Score'] < threshold].copy()
    mismatches = mismatches.sort_values(by='Similarity_Score', ascending=True)

    # Cleanup GPU memory
    del emb_gewerke
    del emb_handwerker
    del t_gewerk_codes
    del t_handwerker_codes
    torch.cuda.empty_cache()

    return mismatches

def handwerker_gewerke_outlier(df):
    df = df[["Handwerker_Name", "Gewerk_Name"]]
    df = df.dropna()
    stats = df.groupby(['Handwerker_Name', 'Gewerk_Name'], observed=True).size().reset_index(name='count')
    total_counts = df.groupby('Handwerker_Name', observed=True).size().reset_index(name='total_count')

    stats = stats.merge(total_counts, on='Handwerker_Name')
    stats['ratio'] = stats['count'] / stats['total_count']

    stats['anzahl_gewerke'] = stats.groupby('Handwerker_Name', observed=True)['Gewerk_Name'].transform('count')
    stats['is_outlier'] = (stats['anzahl_gewerke'] > 1) & (stats['ratio'] < 0.2)
    stats = stats.dropna()

    return stats

def check_keywords_vectorized(df):

    keywords_mapping = {
    'Heizung- und Sanitärinstallation': ['heizung', 'sanitär', 'bad', 'gas', 'wasser', 'hls', 'wärme', 'installateur', 'haustechnik', 'therme', 'leckage'],
    'Metallbau- und Schlosserarbeiten': ['metall', 'schlosser', 'stahlbau', 'schweiß', 'schmiede', 'konstruktion', 'edelstahl'],
    'Fahrrad': ['fahrrad', 'bike', 'rad', 'zweirad', 'velo', 'ebike'],
    'Maurerarbeiten': ['maurer', 'rohbau', 'baugeschäft', 'hochbau', 'bauunternehmung', 'klinker'],
    'Putz- und Stuckarbeiten': ['putz', 'stuck', 'verputz', 'gips', 'lehmbau', 'fassadenputz'],
    'Fassadensysteme': ['fassade', 'verklinkerung', 'dämmung', 'bekleidung', 'wand'],
    'Rollladen und Sonnenschutz': ['rollladen', 'sonnenschutz', 'jalousie', 'markise', 'store', 'beschattung', 'rolltor'],
    'Dachdeckerarbeiten': ['dach', 'bedachung', 'dachdecker', 'steildach', 'flachdach', 'ziegel'],
    'Tief- und Erdbauarbeiten': ['tiefbau', 'erdbau', 'bagger', 'aushub', 'erd bewegung', 'graben', 'schacht'],
    'Bodenbelagsarbeiten': ['boden', 'belag', 'teppich', 'linoleum', 'vinyl', 'raumausstatter', 'laminat', 'designbelag'],
    'Tischlerarbeiten': ['tischler', 'schreiner', 'möbel', 'holzbau', 'innenausbau', 'fensterbau'],
    'Leckageortung und Trocknung': ['leck', 'ortung', 'trocknung', 'feuchte', 'wassersha', 'thermografie'],
    'Fliesen- und Plattenverlegearbeiten': ['fliesen', 'platten', 'mosaik', 'keramik', 'granit', 'steinzeug'],
    'Maler- und Tapezierarbeiten': ['maler', 'lack', 'anstrich', 'tapezier', 'farbe', 'raumdesign'],
    'Zimmer- und Holzbauarbeiten': ['zimmerer', 'zimmerei', 'holzbau', 'sägewerk', 'abbund', 'dachstuhl'],
    'Elektroarbeiten': ['elektro', 'strom', 'elektronik', 'schaltanlagen', 'licht', 'kabel', 'spannung'],
    'Rohr- und Kanalbefahrung': ['kanal', 'rohr', 'tv-inspektion', 'dichtheit', 'abfluss', 'kamera'],
    'Spenglerarbeiten': ['spengler', 'klempner', 'blech', 'flaschner', 'kupfer', 'zink'],
    'Garten- und Landschaftsbauarbeiten': ['garten', 'landschaft', 'galabau', 'grün', 'pflanze', 'baum', 'außenanlagen'],
    'Sachverständigenleistungen': ['sachverständig', 'gutachter', 'expert', 'bewertung', 'wertermittlung', 'analyse'],
    'Multigewerk': ['bauunternehmung', 'generalunternehmer', 'bauservice', 'dienstleistung', 'allround', 'sanierung', 'komplettbau'],
    'Brandschmutzbeseitigung': ['brand', 'sanierung', 'ruß', 'reinigung', 'schadenmanagement'],
    'Verglasungsarbeiten': ['glas', 'fenster', 'vitrinen', 'spiegel', 'wintergarten'],
    'Trockenbauarbeiten': ['trockenbau', 'akustik', 'rigips', 'innenausbau', 'montagebau'],
    'Sicherheits- und Baustelleneinrichtung': ['sicherheit', 'baustrom', 'absperrung', 'bauzaun', 'wc-service', 'logistik'],
    'Abfall, Entsorgung und Recycling': ['entsorgung', 'recycling', 'container', 'schrott', 'abfall', 'mulden'],
    'Schließanlagen und Beschläge': ['schlüssel', 'schließ', 'sicherheitstechnik', 'beschlag', 'tresor'],
    'Daten-, Melde- und Kommunikationsanlagen': ['daten', 'netzwerk', 'kommunikation', 'edv', 'it', 'telekom', 'glasfaser'],
    'Straßen, Wege, Plätze': ['straßenbau', 'pflaster', 'asphalt', 'wege', 'hofbefestigung'],
    'Gebäudereinigung': ['reinigung', 'clean', 'facility', 'sauber', 'glasreinigung', 'service'],
    'Mauerarbeiten': ['mauer', 'stein', 'rohbau', 'sanierung'],
    'Dachklempnerarbeiten': ['dachklempner', 'dachrinne', 'fallrohr', 'bauklempner'],
    'Sanierungsarbeiten an schadstoffhaltigen Bauteilen': ['asbest', 'schadstoff', 'altlasten', 'dekontamination', 'kmf'],
    'Lüftungsbau und Klimatechnik': ['lüftung', 'klima', 'kälte', 'air', 'ventilation', 'raumluft'],
    'Bauleitung': ['bauleitung', 'architekt', 'ingenieur', 'planung', 'baubetreuung', 'projektsteuerung'],
    'Werbeanlagen': ['werbe', 'reklame', 'schild', 'lichtwerbung', 'folie', 'beschriftung', 'sign'],
    'Verkehrstechnische Anlagen': ['verkehr', 'ampel', 'signal', 'markierung', 'leitsystem'],
    'Estricharbeiten': ['estrich', 'unterboden', 'zement', 'fließestrich'],
    'Schwimmbadtechnik': ['schwimmbad', 'pool', 'sauna', 'wellness', 'wasseraufbereitung'],
    'Gerüstbauarbeiten': ['gerüst', 'rüstung', 'einrüstung', 'steigtechnik'],
    'Parkettarbeiten': ['parkett', 'dielen', 'schleif', 'holzboden'],
    'Abbrucharbeiten': ['abbruch', 'abriss', 'rückbau', 'demontage', 'spreng'],
    'Natursteinarbeiten': ['naturstein', 'steinmetz', 'marmor', 'granit', 'grabmale'],
    'Medienverbrauch': ['stadtwerke', 'energie', 'versorgung', 'messdienst', 'strom', 'gas', 'wasser'],
    'Beton- und Stahlbetonarbeiten': ['beton', 'stahlbeton', 'pump', 'fertigteil', 'schalung'],
    'Handel': ['handel', 'vertrieb', 'shop', 'markt', 'baustoff', 'großhandel', 'verkauf'],
    'Mietminderung': ['mieterschutz', 'anwalt', 'mietverein', 'recht'],
    'Stahlbauarbeiten': ['stahlbau', 'halle', 'tragwerk', 'schlosserei'],
    'Betonerhaltungsarbeiten': ['betonsanierung', 'bautenschutz', 'rissinjizierung', 'oberflächenschutz'],
    'Wasserhaltung': ['wasserhaltung', 'grundwasser', 'absenkung', 'brunnenbau'],
    'Solaranlagen': ['solar', 'photovoltaik', 'pv', 'sonne', 'regenerativ', 'energie'],
    'Schutz- und Bewegungsaufwand': ['schutz', 'verpackung', 'abdeckung', 'transportschutz', 'umzug'],
    'Rechtsanwälte': ['anwalt', 'kanzlei', 'recht', 'notar', 'law', 'jurist'],
    'Abdichtungsarbeiten gegen Wasser/ Bauwerkstrockenlegung': ['abdichtung', 'isolierung', 'bitumen', 'injektion', 'trockenlegung', 'leckage'],
    'Zäune und Grundstückseinfriedungen': ['zaun', 'tor', 'einfriedung', 'gitter', 'draht'],
    'Bekämpfender Holzschutz': ['holzschutz', 'schwamm', 'schädlingsbekämpfung', 'kammerjäger'],
    'Spengler- / Klempnerarbeiten': ['spengler', 'klempner', 'flaschner', 'blechbearbeitung', 'leckage'],
    'Trocknung': ['trocknung', 'bautrocknung', 'entfeuchtung', 'leckage'],
    'KFZ': ['kfz', 'auto', 'werkstatt', 'car', 'motor', 'fahrzeug', 'garage'],
    'Leckageortung': ['leckage', 'ortung', 'rohrbruch', 'leck'],
    'Immobilien': ['immobilien', 'makler', 'wohnbau', 'real estate', 'verwaltung', 'property'],
    'Versicherung': ['versicherung', 'finanz', 'assekuranz', 'makler', 'agentur']
    }



    names = df['Handwerker_Name'].astype(str).str.lower()

    confirmed_mask = np.zeros(len(df), dtype=bool)

    conflict_series = pd.Series([None] * len(df), index=df.index)

    for trade, keywords in keywords_mapping.items():
        if not keywords:
            continue

        pattern = '|'.join(map(re.escape, keywords))

        has_keyword = names.str.contains(pattern, regex=True, na=False)

        is_current_trade = (df['Gewerk_Name'] == trade)
        confirmed_mask = confirmed_mask | (has_keyword & is_current_trade)

        is_conflict = (has_keyword & ~is_current_trade)

        mask_to_update = is_conflict & conflict_series.isna()
        conflict_series.loc[mask_to_update] = f"CONFLICT_WITH_{trade.upper()}"

    final_result = np.where(
        confirmed_mask,
        "CONFIRMED_BY_NAME",
        np.where(
            conflict_series.notna(),
            conflict_series,
            "NO_KEYWORD_INFO"
        )
    )

    return final_result


def abgleich_auftraege(df1, df2):
    """
    Vergleicht die Kopfdaten von Aufträgen (df1) mit der Summe ihrer Positionen (df2).

    Die Funktion gruppiert die Positionsdaten (df2) anhand der 'Kva_RechnungID', bildet
    die Summen für 'Forderung_Netto' und 'Einigung_Netto' und vergleicht diese mit den
    in df1 hinterlegten Werten. Gleitkomma-Ungenauigkeiten werden dabei berücksichtigt.

    Args:
        df1 (pd.DataFrame): Dataframe mit den Auftragsdaten (Soll-Werte).
            Muss zwingend folgende Spalten enthalten:
            - 'Kva_RechnungID' (Verbindungsschlüssel)
            - 'Forderung_Netto'
            - 'Einigung_Netto'
            
        df2 (pd.DataFrame): Dataframe mit den Positionsdaten (Ist-Werte).
            Muss zwingend folgende Spalten enthalten:
            - 'Kva_RechnungID' (Verbindungsschlüssel)
            - 'Forderung_Netto'
            - 'Einigung_Netto'

    Returns:
        pd.DataFrame: Eine Liste der Abweichungen. Der Dataframe enthält nur die IDs,
        bei denen die Werte nicht übereinstimmen.
        
        Enthaltene Spalten:
        - 'Kva_RechnungID': ID des betroffenen Auftrags.
        - 'Diff_Forderung': Differenzbetrag (Wert in df1 - Summe in df2).
        - 'Diff_Einigung': Differenzbetrag (Wert in df1 - Summe in df2).
        
        Ist die Differenz positiv, ist der Wert im Auftrag höher als die Summe der Positionen.
    """

    df2_sum = df2.groupby('KvaRechnung_ID', observed=False)[['Forderung_Netto', 'Einigung_Netto']].sum().reset_index()

    merged = pd.merge(df1, df2_sum, on='KvaRechnung_ID', how='left', suffixes=('_soll', '_ist'))

    cols_to_fix = ['Forderung_Netto_ist', 'Einigung_Netto_ist']
    merged[cols_to_fix] = merged[cols_to_fix].fillna(0)

    merged['Diff_Forderung'] = (merged['Forderung_Netto_soll'] - merged['Forderung_Netto_ist']).round(2)
    merged['Diff_Einigung'] = (merged['Einigung_Netto_soll'] - merged['Einigung_Netto_ist']).round(2)

    mask_abweichung = (
        ~np.isclose(merged['Diff_Forderung'], 0) |
        ~np.isclose(merged['Diff_Einigung'], 0)
    )

    abweichungen = merged[mask_abweichung].copy()

    result_df = abweichungen[['KvaRechnung_ID', 'Diff_Forderung', 'Diff_Einigung','CRMEingangszeit']]

    return result_df


def get_fn_df1_details(df):
    """Calculates detailed statistics and specific error instances for the 'Tripel-Vorzeichen' check in 'Auftragsdaten'.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing 'Auftragsdaten' data set that is to be evaluated.

    Returns
    -------
    stats_df: pandas.DataFrame
        Small DataFrame containing error counts per column (Einigung, Empfehlung, Forderung) for visualization.
    details_df: pandas.DataFrame
        DataFrame containing the top 500 most severe error instances.
    """
    m_ein = (df['Einigung_Netto'] < 0)
    m_emp = (df["Empfehlung_Netto"] < 0)
    m_for = (df["Forderung_Netto"] < 0)

    e_ein = m_ein & ~(m_for & m_emp)
    e_emp = m_emp & ~(m_for & m_ein)
    e_for = m_for & ~(m_ein & m_emp)

    stats_df = pd.DataFrame({
        "Spalte": ["Einigung_Netto", "Empfehlung_Netto", "Forderung_Netto"],
        "Fehler": [int(e_ein.sum()), int(e_emp.sum()), int(e_for.sum())]
    })

    full_mask = e_ein | e_emp | e_for
    details_df = df.loc[full_mask, ["KvaRechnung_ID", "Forderung_Netto", "Empfehlung_Netto", "Einigung_Netto"]].copy()
    if not details_df.empty:
        details_df["Schwere"] = details_df[["Forderung_Netto", "Empfehlung_Netto", "Einigung_Netto"]].abs().max(axis=1)
        details_df = details_df.sort_values("Schwere", ascending=False)

    return stats_df, details_df


def get_fn_df2_details(df2):
    """Calculates detailed statistics and specific error instances for consistency checks in 'Positionsdaten'.

    Parameters
    ----------
    df2 : pandas.DataFrame
        DataFrame containing 'Positionsdaten' data set that is to be evaluated.

    Returns
    -------
    stats_df: pandas.DataFrame
        DataFrame containing error counts per category (e.g. 'Menge < 0', 'Vorzeichen Mismatch').
    details_df: pandas.DataFrame
        DataFrame containing specific error instances (e.g. sign mismatches).
    """
    errors_list = []

    if "Menge" in df2.columns:
        c = (df2['Menge'] < 0).sum()
        if c > 0: errors_list.append({"Kategorie": "Menge < 0", "Anzahl": int(c)})

    if "Menge_Einigung" in df2.columns:
        c = (df2['Menge_Einigung'] < 0).sum()
        if c > 0: errors_list.append({"Kategorie": "Menge_Einigung < 0", "Anzahl": int(c)})

    mask_ep = (df2['EP'] < 0) ^ (df2['EP_Einigung'] < 0)
    if mask_ep.sum() > 0:
        errors_list.append({"Kategorie": "Vorzeichen EP ungleich", "Anzahl": int(mask_ep.sum())})

    mask_betrag = (df2['Forderung_Netto'] < 0) ^ (df2['Einigung_Netto'] < 0)
    if mask_betrag.sum() > 0:
        errors_list.append({"Kategorie": "Vorzeichen Betrag ungleich", "Anzahl": int(mask_betrag.sum())})

    stats_df = pd.DataFrame(errors_list)

    details_df = pd.DataFrame()
    if mask_betrag.any():
        cols = ["Position_ID", "Forderung_Netto", "Einigung_Netto", "Menge", "Bezeichnung"]

        if "Position_ID" not in df2.columns:
            temp_df = df2.loc[mask_betrag].copy()
            if "Position_ID" not in temp_df.columns:
                temp_df = temp_df.reset_index()
                if "index" in temp_df.columns:
                    temp_df = temp_df.rename(columns={"index": "Position_ID"})
        else:
            temp_df = df2.loc[mask_betrag]

        available_cols = [c for c in cols if c in temp_df.columns]
        details_df = temp_df[available_cols]

    return stats_df, details_df


def get_discount_details(df2):
    """Aggregates statistics on discount logic errors and returns detailed instances based on the 'Plausibel' column.

    Parameters
    ----------
    df2 : pandas.DataFrame
        DataFrame containing 'Positionsdaten' data set that is to be evaluated.

    Returns
    -------
    stats_df: pandas.DataFrame
        DataFrame with counts of the most frequent descriptions (Bezeichnung) among invalid entries.
    details_df: pandas.DataFrame
        DataFrame containing specific invalid rows.
    """
    if "Plausibel" not in df2.columns:
        return pd.DataFrame(), pd.DataFrame()

    mask_err = ~df2["Plausibel"]

    stats_df = pd.DataFrame()
    if mask_err.any() and "Bezeichnung" in df2.columns:
        stats_df = df2.loc[mask_err, "Bezeichnung"].value_counts().head(15).reset_index()
        stats_df.columns = ["Bezeichnung", "Anzahl"]

    cols = ["Position_ID", "Bezeichnung", "Forderung_Netto", "Einigung_Netto", "ist_Abzug"]
    details_df = df2.loc[mask_err, [c for c in cols if c in df2.columns]]

    return stats_df, details_df


# def get_plausi_outliers(df):
#     """Identifies the most significant outliers for the check 'Einigung > Forderung' in 'Auftragsdaten'.

#     Parameters
#     ----------
#     df : pandas.DataFrame
#         DataFrame containing 'Auftragsdaten' data set that is to be evaluated.

#     Returns
#     -------
#     top_outliers: pandas.DataFrame
#         DataFrame containing all entries with the highest positive difference (Einigung - Forderung).
#     """
#     cols = ["KvaRechnung_ID", "Forderung_Netto", "Einigung_Netto"]
#     df_res = df[cols].copy()

#     df_res["Diff"] = df_res["Einigung_Netto"] - df_res["Forderung_Netto"]

#     df_res = df_res[df_res["Diff"] > 0]

#     outliers = df_res.sort_values(by="Diff", ascending=False)
#     return outliers


# def get_plausi_outliers_df2(df2):
#     """Identifies the most significant outliers for the check 'Einigung > Forderung' in 'Positionsdaten'.

#     Parameters
#     ----------
#     df2 : pandas.DataFrame
#         DataFrame containing 'Positionsdaten' data set that is to be evaluated.

#     Returns
#     -------
#     top_outliers: pandas.DataFrame
#         DataFrame containing all entries with the highest positive difference (Einigung - Forderung).
#     """
#     cols = ["Position_ID", "Forderung_Netto", "Einigung_Netto"]

#     df_res = df2[cols].copy()

#     df_res["Diff"] = df_res["Einigung_Netto"] - df_res["Forderung_Netto"]
#     df_res = df_res[df_res["Diff"] > 0]

#     outliers = df_res.sort_values(by="Diff", ascending=False)
#     return outliers

if __name__ == "__main__":
    df, df2 = load_data()

    print(plausibilitaetscheck_forderung_einigung(df2))