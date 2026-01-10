import streamlit as st


def show_page(df, df2, metrics_df1, metrics_df2, metrics_combined):
    df_outlier = metrics_df1.get("handwerker_gewerke_outlier")
    # mismatched_entries = metrics_df1.get("mismatched_entries")
    kundengruppe_containing_test = metrics_df1.get("test_kundengruppen_anzahl")
    anteil = kundengruppe_containing_test / len(df) * 100

    # outlier KPI
    outlier_count = 0 if df_outlier is None else len(df_outlier)
    outlier_share = outlier_count / len(df) * 100 if len(df) else 0

    kpi_cols = st.columns(2)
    with kpi_cols[0]: st.metric(
        label="Testdatensätze in Kundengruppe",
        value=f"{kundengruppe_containing_test}",
        delta=f"{anteil:.2f}% der Datensätze",
        delta_color="off"
    )

    with kpi_cols[1]:
        st.metric(
            label="Auffällige Handwerker - Gewerk Zuordnungen",
            value=str(outlier_count),
            delta=f"{outlier_share:.2f}% der Datensätze",
            delta_color="off"
        )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Zuordnung Handwerker/Gewerk mit Embeddings + Cosine Distance")
        #st.dataframe(mismatched_entries)

    with chart_col2:
        st.subheader("Zuordnung Handwerker/Gewerke Regelbasiert")
        st.dataframe(df_outlier)