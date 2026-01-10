import pandas as pd
import numpy as np
from sklearn import datasets
from evidently import Dataset
from evidently import DataDefinition
from evidently import Report
from evidently.presets import DataDriftPreset, DataSummaryPreset
import streamlit as st
import streamlit.components.v1 as components
import pyinstrument as pyins


#TODO: remove streamlit components when done as module
#@st.cache_data
@pyins.profile()
def load():
    df = pd.read_parquet("resources/Auftragsdaten_konvertiert")
    df2 = pd.read_parquet("resources/Positionsdaten_konvertiert")
    df = df.sort_values("CRMEingangszeit", ascending=True)
    df2 = pd.merge(df2,df[['KvaRechnung_ID','CRMEingangszeit']], on='KvaRechnung_ID', how='left')
    df2 = df2.sort_values("CRMEingangszeit", ascending=True)
    return df, df2

df, df2 = load()
#st.write("Load done")
print("Load finished")

#about 4300 entries without a time label, these get dropped
df = df.dropna(subset=['CRMEingangszeit'])
df2 = df2.dropna(subset=['CRMEingangszeit'])

# Schema für Auftragsdatenset, nur aufgeführte Spalten werden geprüft   
schema_df1 = DataDefinition(
    numerical_columns= ["Forderung_Netto", "Empfehlung_Netto", "Einigung_Netto", "Differenz_vor_Zeitwert_Netto"],
    categorical_columns= ["Land","Schadenart_Name", "Falltyp_Name", "Gewerk_Name"],
    id_column= "AuftragID",
    timestamp= "CRMEingangszeit"
) 
#Analog für Positionsdaten
schema_df2 = DataDefinition(
    id_column= "Position_ID",
    numerical_columns= ["Menge","Menge_Einigung", "EP", "EP_Einigung", "Forderung_Netto", "Einigung_Netto", "Position_ID"],
    timestamp="CRMEingangszeit"
    )


    
   


#Test-Initialisierung von Datensets 
# reference_data1 = Dataset.from_pandas(
#     df.head(2000),
#     data_definition=schema_df1
# )    
# eval_data1 = Dataset.from_pandas(
#     df.head(10000),
#     data_definition=schema_df1
# )     



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



@pyins.profile()
def datetime_slice_mask(df, start_date, end_date):
    """Helper function. Returns a chronologically sliced Dataset according to passed datetime.

    Parameters
    ----------
    df : pandas.Dataframe
        input df
    start_date : datetime
    
    end_date : datetime
      

    Returns
    -------
    evidently.Dataset
        sliced DataFrame, converted to Dataset.
    """
    mask =(df["CRMEingangszeit"] >= start_date) & (df["CRMEingangszeit"] < end_date) 
    sliced_ds = Dataset.from_pandas(
        df.loc[mask]
    ) 
    return sliced_ds

@pyins.profile()
def data_drift_evaluation(df, start_date_reference, end_date_reference, start_date_eval, end_date_eval):
    """Uses the standard preset in the evidentlyai framework to evaluate data drift between two samples (chosen by time interval) from the passed DataFrame. The resulting Snapshot object is saved as html for easy embedding.

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
        my_eval.save_html("resources/eval_df.html")
    if 'Menge' in df.columns: #evaluates true if Positionsdaten-df was passed
        report = Report([
            DataDriftPreset(
                columns=["Menge","Menge_Einigung", "EP", "EP_Einigung", "Forderung_Netto", "Einigung_Netto"]
                )
        ])
        my_eval = report.run(eval_data, reference_data)
        my_eval.save_html("resources/eval_df2.html")     


test_start_time_ref= pd.to_datetime("2023-02-01 01:01:01")
test_start_time_eval= pd.to_datetime("2023-06-02 01:01:01")
test_end_time_ref = pd.to_datetime("2023-06-01 00:00:00")
test_end_time_eval = pd.to_datetime("2023-12-01 00:00:00") 
print("Starting eval of df1")
data_drift_evaluation(df, test_start_time_ref,test_end_time_ref,test_start_time_eval,test_end_time_eval)
print("finished df1")
data_drift_evaluation(df2, test_start_time_ref,test_end_time_ref,test_start_time_eval,test_end_time_eval)

eval_df_html= open("resources/eval_df.html", "r", encoding="utf-8").read()
eval_df2_html= open("resources/eval_df2.html", "r", encoding="utf-8").read()



# components.html(eval_df_html,scrolling=True)
# components.html(eval_df2_html, scrolling=True)
