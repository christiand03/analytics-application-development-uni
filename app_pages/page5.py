import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import data_drift_metrics as ddm
import duckdb
from pathlib import Path

@st.cache_data
def load_df(df_type): 
    """Loads the full specified DataFrame from the database into cache.

    Parameters
    ----------
    df_type : string
        expects df for order data, df2 for position data

    Returns
    -------
    pandas.DataFrame
        order or position DataFrame
    """
    con = duckdb.connect("resources/dashboard_data.duckdb", read_only=True)
    if df_type == "df":
        try:
            df = con.execute("SELECT * FROM auftragsdaten").df()
        finally:
            con.close() 
    if df_type == "df2":
        try:
            df = con.execute("SELECT * FROM positionsdaten").df()   
        finally:
             con.close()
    return df

def fetch_reports_table():
    """Generates a DataFrame containing the timestamp ranges of all saved reports and the respective data source.

    Returns
    -------
    pandas.DataFrame   
    """
    reports_folder = Path("resources/reports")
    filenames = [f.stem for f in reports_folder.iterdir() if f.is_file()]
    split = [name.split("_")for name in filenames]
    df_reports = pd.DataFrame(split, columns=["eval", "Quelle", "Start Ref.", "Ende Ref.", "Start Vergl.", "Ende Vergl."])
    #date_col = ["Start Ref.", "Ende Ref.", "Start Vergl.", "Ende Vergl."]
    #df_reports[date_col]= df_reports[date_col].apply(pd.to_datetime, errors="coerce")
    df_reports= df_reports.drop(["eval"], axis="columns")
    df_reports=df_reports.replace({"Quelle":{"df":"Aufträge","df2":"Positionen"}})
    return df_reports
    
def refresh_table():
    #helper function to update the report listing as displayed in the dashboard 
     st.session_state.reports_table = fetch_reports_table()

def show_page():
    """This function renders page 5 of 5 of the dashboard.

    Page 5 lets you generate data drift reports and embeds them.
    Generated reports can be found at ./resources/reports .
    

    Notes
    -----

    For implementation details of the report generation process and customization options, please refer to data_drift_metrics.py
    and it's documentation.     
    """
    con = duckdb.connect("resources/dashboard_data.duckdb", read_only=True)
   
    try:
        #limit date selection options to observed timestamp ranges
        min_date = con.execute("SELECT MIN(CRMEingangszeit) FROM auftragsdaten").fetchone()[0].date()
        max_date = con.execute("SELECT MAX(CRMEingangszeit) FROM auftragsdaten").fetchone()[0].date()
    finally:
         con.close()    
    min_date_6m = min_date + pd.Timedelta(weeks=26)
    min_date_12m = min_date + pd.Timedelta(weeks=52)
    report_html= None
    path_to_report = None
    
    
    form_column, tab_column = st.columns(2)
    dynamic_reset_ph = tab_column.empty() # forces streamlit to refresh the report list on reload
    with form_column:
        #Date-Picker, für Referenzset und Evalset, Quelldatenset
        with st.expander("Reportauswahl", width=750):
            with st.form("Vergleichszeiträume"):
            
                source_designation = st.selectbox(
                    "Datenquelle",
                    ("Auftragsdaten", "Positionsdaten"),
                    width=175
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    start_date_reference, end_date_reference = st.date_input(
                        "Referenzrahmen",
                        (min_date,min_date_6m),
                        min_date,max_date, 
                        width=225                                   
                        )
                with col2:    
                    start_date_eval, end_date_eval = st.date_input(
                        "Vergleichsrahmen",
                        (min_date_6m,min_date_12m),
                        min_date,max_date,
                        width=225
                        )
                    
                force_reload = st.checkbox("Refresh erzwingen?")

                submitted = st.form_submit_button("Report anzeigen")

                if submitted:
                #gives feedback on selected report file location
                    st.write("Pfad zum Report:")
                    if source_designation == "Auftragsdaten":
                            source_type = "df"
                            path_to_report = f"resources/reports/eval_df_{str(start_date_reference)}_{str(end_date_reference)}_{str(start_date_eval)}_{str(end_date_eval)}.html"
                            st.code("./"+path_to_report)
                    if source_designation == "Positionsdaten":
                            source_type = "df2"
                            path_to_report = ("resources/reports/eval_df2_"+
                                                            str(start_date_reference)+"_"+
                                                            str(end_date_reference)+"_"+
                                                            str(start_date_eval)+"_"+
                                                            str(end_date_eval)+
                                                            ".html") 
                            st.code("./"+path_to_report)
                    if force_reload:
                            st.write("-> Report wird neu erstellt <-")
    
    with dynamic_reset_ph:
        with st.expander("Verfügbare Reports", width= 750):
            refresh_table()
            st.dataframe(st.session_state.reports_table)                                 

    #prevents use of uninitialized values further down the line    
    if not path_to_report:
         st.write("Warten auf Auswahl..")
         st.stop()

         
    try: #try loading the selected report from disk 
        if not force_reload:
            report_html = open(path_to_report, "r", encoding="utf-8").read()
            components.html(report_html, height= 1000, scrolling=True)
        else:
             raise FileNotFoundError    
    except FileNotFoundError: #if loading fails or recompute was selected, compute and save report as html
        with st.empty():
            source_df = load_df(source_type).dropna(subset=['CRMEingangszeit'])
            st.write("Report ist noch nicht vorhanden und wird erstellt. Dies kann einige Momente dauern...")
            ddm.data_drift_evaluation(
                source_df, 
                start_date_reference, end_date_reference,
                start_date_eval, end_date_eval
                )
            st.write("Report erstellt.")
        report_html = open(path_to_report, "r", encoding="utf-8").read()    
        components.html(report_html, height= 1000, scrolling=True)
    
    #refresh reports list after report generation
    dynamic_reset_ph.empty()
    with tab_column:
        with st.expander("Verfügbare Reports", width= 750):
            refresh_table()
            st.dataframe(st.session_state.reports_table)    
    

    
    












    


