import streamlit as st


def show_page(metrics_df1, metrics_df2, metrics_combined, comparison_df=None):

    # Helperfunction to get delta from comparison_df
    def get_delta(metric_name):
        if comparison_df is None or comparison_df.empty:
            return None
        
        row = comparison_df[comparison_df['Metric'] == metric_name]
        
        if not row.empty:
            val = row.iloc[0]['Percent_Change']
            return f"{val:+.2f}%"
        return None


    df_outlier = metrics_df1.get("handwerker_gewerke_outlier")
    # mismatched_entries = metrics_df1.get("mismatched_entries")
    kundengruppe_containing_test = metrics_df1.get("test_kundengruppen_anzahl")
    row_count = metrics_df1.get("row_count")
    anteil = kundengruppe_containing_test / row_count * 100

    # outlier KPI
    outlier_count = 0 if df_outlier is None else len(df_outlier[df_outlier['is_outlier'] == True])
    outlier_share = outlier_count / row_count * 100

    kpi_cols = st.columns(2)
    with kpi_cols[0]: st.metric(
        label="Testdatensätze in Kundengruppe",
        value=f"{kundengruppe_containing_test}",
        delta=f"{anteil:.2f}% der Datensätze",
        delta_color="inverse"
    )

    with kpi_cols[1]:
        st.metric(
            label="Auffällige Handwerker - Gewerk Zuordnungen",
            value=str(outlier_count),
            delta=f"{outlier_share:.2f}% der Datensätze",
            delta_color="inverse"
        )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Zuordnung Handwerker/Gewerk mit Embeddings + Cosine Distance")
        #st.dataframe(mismatched_entries)

    with chart_col2:
        st.subheader("Zuordnung Handwerker/Gewerke Regelbasiert")
        st.dataframe(df_outlier)