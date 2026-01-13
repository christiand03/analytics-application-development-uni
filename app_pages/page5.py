import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import data_drift_metrics as ddm

# TODO:Alternative für duckdb schreiben, mit fetch nur bei bedarf
def show_page(df, df2, metrics_df1, metrics_df2, metrics_combined):
    st.title("Data Drift Reports")
    min_date = df["CRMEingangszeit"].min().date()
    max_date = df["CRMEingangszeit"].max().date()
    min_date_6m = df["CRMEingangszeit"].min().date() + pd.Timedelta(weeks=26)
    min_date_12m = df["CRMEingangszeit"].min().date() + pd.Timedelta(weeks=52)
    report_html= None
    path_to_report = None
    #Date-Picker, für Referenzset und Evalset, Quelldatenset
    with st.expander("Reportauswahl"):
        with st.form("Vergleichszeiträume"):
        
            source_designation = st.selectbox(
                "Datenquelle",
                ("Auftragsdaten", "Positionsdaten"),
                )
            
            col1, col2 = st.columns(2)
            with col1:
                start_date_reference, end_date_reference = st.date_input(
                    "Referenzrahmen",
                    (min_date,min_date_6m),
                    min_date,max_date                                   
                    )
            with col2:    
                start_date_eval, end_date_eval = st.date_input(
                    "Vergleichsrahmen",
                    (min_date_6m,min_date_12m),
                    min_date,max_date
                    )
                
            force_reload = st.checkbox("Refresh erzwingen?")

            submitted = st.form_submit_button("Report anzeigen")

            if submitted:
            #Check für den Ordnerpfad
                st.write("Pfad zum Report:")
                if source_designation == "Auftragsdaten":
                        source_df = df.dropna(subset=['CRMEingangszeit'])
                        path_to_report = f"resources/reports/eval_df_{str(start_date_reference)}_{str(end_date_reference)}_{str(start_date_eval)}_{str(end_date_eval)}.html"
                        st.code("./"+path_to_report)
                if source_designation == "Positionsdaten":
                        source_df = df2.dropna(subset=['CRMEingangszeit'])
                        path_to_report = ("resources/reports/eval_df2_"+
                                                        str(start_date_reference)+"_"+
                                                        str(end_date_reference)+"_"+
                                                        str(start_date_eval)+"_"+
                                                        str(end_date_eval)+
                                                        ".html") 
                        st.code("./"+path_to_report)
                if force_reload:
                        st.write("-> Report wird neu erstellt <-")

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
            st.write("Report ist noch nicht vorhanden und wird erstellt. Dies kann einige Momente dauern...")
            ddm.data_drift_evaluation(
                source_df, 
                start_date_reference, end_date_reference,
                start_date_eval, end_date_eval
                )
            st.write("Report erstellt.")
        report_html = open(path_to_report, "r", encoding="utf-8").read()    
        components.html(report_html, height= 1000, scrolling=True)
    

    
    












    


