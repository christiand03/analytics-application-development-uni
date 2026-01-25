import pandas as pd
from evidently import Dataset
from evidently import DataDefinition
from evidently import Report
from evidently.presets import DataDriftPreset

# Schema für Auftragsdatenset, nur aufgeführte Spalten werden geprüft   
schema_df = DataDefinition(
    numerical_columns= ["Forderung_Netto", "Empfehlung_Netto", "Einigung_Netto", "Differenz_vor_Zeitwert_Netto"],
    categorical_columns= ["Land","Schadenart_Name", "Falltyp_Name", "Gewerk_Name"],
    id_column= "AuftragID",
    timestamp= "CRMEingangszeit"
) 
#Analog für Positionsdaten
schema_df2 = DataDefinition(
    id_column= "Position_ID",
    numerical_columns= ["Menge","Menge_Einigung", "EP", "EP_Einigung", "Forderung_Netto", "Einigung_Netto"],
    timestamp="CRMEingangszeit"
    )

def check_start_end_date(start,end):
    """Helper function. Checks if end follows start chronologically and reorders the two if needed. 

    Parameters
    ----------
    start : datetime
        The assumed beginnig of the interval.
    end : datetime
        The assumed end of the interval.

    Returns
    -------
    datetime, datetime
        Pair of chronologically sorted datetime values.
    """
    if(start > end):
       start, end = end, start
    return start, end


def datetime_slice_mask(df, start_date, end_date):
    """Helper function. Returns a chronologically sliced Dataset according to passed datetime.

    Parameters
    ----------
    df : pandas.Dataframe
        input df
    start_date : date
    
    end_date : date
      

    Returns
    -------
    evidently.Dataset
        sliced DataFrame, converted to Dataset.
    """
    #Type cleanup to full datetime, due to the dashboard passing only date-level precision values
    start_date = pd.to_datetime(start_date).replace(hour=0,minute=0,second=0)
    end_date = pd.to_datetime(end_date).replace(hour=0,minute=0,second=0) 

    mask =(df["CRMEingangszeit"] >= start_date) & (df["CRMEingangszeit"] < end_date)

    if 'Kundengruppe' in df.columns: #evaluates true if Auftragsdaten-df was passed 
        sliced_ds = Dataset.from_pandas(
            df.loc[mask],
            data_definition=schema_df
        ) 
    if 'Menge' in df.columns: #evaluates true if Positionsdaten-df was passed
        sliced_ds = Dataset.from_pandas(
            df.loc[mask],
            data_definition=schema_df2
        )  
    return sliced_ds


def data_drift_evaluation(df, start_date_reference, end_date_reference, start_date_eval, end_date_eval):
    """Generates a evidentlyAI data drift report Snapshot object.
    
      This function uses the standard preset in the evidentlyai framework to evaluate data drift between two samples (chosen by time interval) from the passed DataFrame.
      The resulting Snapshot object is saved as html for easy embedding.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to sample from
    start_date_reference : datetime
        starting datetime of the reference, baseline dataset
    end_date_reference : datetime
        ending datetime of the reference, baseline dataset
    start_date_eval : datetime
        starting datetime of the evaluated dataset 
    end_date_eval : datetime
        starting datetime of the evaluated dataset
    
    Notes
    -----
    Evidently's default preset uses the Wasserstein distance for numerical features and the Jensen-Shannon divergence for data sets with >1000 observations.
    If you wish to customize methods used or the threshold for drift detection, simply add the respective arguments for the DataDriftPreset class as 
    detailed in https://docs.evidentlyai.com/metrics/customize_data_drift. 

    """
    #check if start and end dates are in chronologicl order, switch if needed
    start_date_reference, end_date_reference = check_start_end_date(start_date_reference, end_date_reference)
    start_date_eval, end_date_eval = check_start_end_date(start_date_eval, end_date_eval)
    
    #create sliced datasets for analysis (mask-based)
    reference_data = datetime_slice_mask(df,start_date_reference,end_date_reference)
    eval_data = datetime_slice_mask(df, start_date_eval,end_date_eval) 
    
    if 'Kundengruppe' in df.columns: #evaluates true if Auftragsdaten-df was passed
        report = Report([
            DataDriftPreset(
                columns=["Forderung_Netto", "Empfehlung_Netto", "Einigung_Netto", "Differenz_vor_Zeitwert_Netto","Land","Schadenart_Name", "Falltyp_Name", "Gewerk_Name"]
                )
        ])
        my_eval = report.run(eval_data, reference_data)
        my_eval.save_html("resources/reports/eval_df_"+
                          str(start_date_reference)+"_"+
                          str(end_date_reference)+"_"+
                          str(start_date_eval)+"_"+
                          str(end_date_eval)+
                          ".html")
    if 'Menge' in df.columns: #evaluates true if Positionsdaten-df was passed
        report = Report([
            #add arguments here to customize reports
            DataDriftPreset(
                #consider only the following columns 
                columns=["Menge","Menge_Einigung", "EP", "EP_Einigung", "Forderung_Netto", "Einigung_Netto"]
                )
        ])
        my_eval = report.run(eval_data, reference_data)
        my_eval.save_html("resources/reports/eval_df2_"+
                          str(start_date_reference)+"_"+
                          str(end_date_reference)+"_"+
                          str(start_date_eval)+"_"+
                          str(end_date_eval)+
                          ".html")     


