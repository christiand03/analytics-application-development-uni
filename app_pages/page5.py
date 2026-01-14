import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import data_drift_metrics as ddm
import duckdb
from pathlib import Path

@st.cache_data
def load_df(df_type): #wäre es schneller die nulls schon hier im SQL zu droppen?
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
     st.session_state.reports_table = fetch_reports_table()

# TODO:Alternative für duckdb schreiben, mit fetch nur bei bedarf
def show_page(metrics_df1, metrics_df2, metrics_combined, comparison_df):
    con = duckdb.connect("resources/dashboard_data.duckdb", read_only=True)
   
    try:
        min_date = con.execute("SELECT MIN(CRMEingangszeit) FROM auftragsdaten").fetchone()[0].date()
        max_date = con.execute("SELECT MAX(CRMEingangszeit) FROM auftragsdaten").fetchone()[0].date()
    finally:
         con.close()    
    min_date_6m = min_date + pd.Timedelta(weeks=26)
    min_date_12m = min_date + pd.Timedelta(weeks=52)
    report_html= None
    path_to_report = None
    
    
    form_column, tab_column = st.columns(2)
    dynamic_reset_ph = tab_column.empty()
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
                #Check für den Ordnerpfad
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

         
    try: #versuche den gewünschten report zu finden
        if not force_reload:
            report_html = open(path_to_report, "r", encoding="utf-8").read()
            components.html(report_html, height= 1000, scrolling=True)
        else:
             raise FileNotFoundError    
    except FileNotFoundError: #erstelle fehlenden report, dazu feedback
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
    
    dynamic_reset_ph.empty()
    with tab_column:
        with st.expander("Verfügbare Reports", width= 750):
            refresh_table()
            st.dataframe(st.session_state.reports_table)    
    

    
    












    


