import streamlit as st


def show_page(df, df2, metrics_df1, metrics_df2, metrics_combined):
    
    df_outlier = metrics_df1.get("handwerker_gewerke_outlier")
    #mismatched_entries = metrics_df1.get("mismatched_entries")
    kundengruppe_containing_test = metrics_df1.get("test_kundengruppen_anzahl")

    kpi_cols = st.columns(2)
    with kpi_cols[0]: st.metric(label="Anzahl Testdatensätze in Kundengruppe", value=kundengruppe_containing_test)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Zuordnung Handwerker/Gewerk mit Embeddings + Cosine Distance")
        #st.dataframe(mismatched_entries)

    with chart_col2:
        st.subheader("Zuordnung Handwerker/Gewerke Regelbasiert")
        st.dataframe(df_outlier)