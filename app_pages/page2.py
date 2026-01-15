import streamlit as st
import pandas as pd
import altair as alt

def show_page(metrics_df1, metrics_df2, metrics_combined, comparison_df, issues_df):

    # Helperfunction to get delta from comparison_df
    def get_delta(metric_name):
        if comparison_df is None or comparison_df.empty:
            return None
        
        row = comparison_df[comparison_df['Metric'] == metric_name]
        
        if not row.empty:
            val = row.iloc[0]['Percent_Change']
            return f"{val:+.2f}%"
        return None

    zeitwert_error_df = metrics_df1.get("zeitwert_error_df", pd.NA)
    zeitwert_error_count = metrics_df1.get("zeitwert_errors_count", pd.NA)
    above_50k_df = metrics_df1.get("above_50k_df", pd.NA)
    above_50k_count = len(above_50k_df)
    row_count = metrics_df1.get("row_count")
    row_count_df2 = metrics_df2.get("row_count")
    auftraege_abgleich = metrics_combined.get("auftraege_abgleich")
    numeric_issues = issues_df["numeric_issues"]

    anteil_zeitwert = (zeitwert_error_count / row_count) * 100 
    anteil_above_50k = (above_50k_count / row_count) * 100 
    anteil_summe = (auftraege_abgleich.shape[0] / row_count) * 100 
    anteil_numeric_issues = (numeric_issues / (row_count + row_count_df2)) * 100
    print(type(anteil_numeric_issues))

    # --- KPIs ---
    kpi_cols = st.columns(4)
    with kpi_cols[0]: 
        st.metric(label="Numerische Auffälligkeiten", value=numeric_issues, delta=get_delta("numeric_issues"), delta_color="inverse", help="Numerische Fehler und Warnings im Datensatz")
        st.caption(f"Anteil: {anteil_numeric_issues:.2f}% relevanter Datensätze (beide Datensätze)")
    with kpi_cols[1]: 
        st.metric(label="Fehleranzahl Zeitwerte", value=zeitwert_error_count, delta=get_delta("count_zeitwert_errors"), delta_color="inverse", help="Anzahl der Fehler in Zeitwertspalte")
        st.caption(f"Anteil: {anteil_zeitwert:.2f}% relevanter Datensätze (Auftragsdaten)")
    with kpi_cols[2]: 
        st.metric(label="Anzahl Aufträge über 50.000€", value=above_50k_count, delta=get_delta("count_above_50k"), delta_color="inverse", help="Anzahl der Aufträge mit einem Wert über 50.000€")
        st.caption(f"Anteil: {anteil_above_50k:.2f}% relevanter Datensätze (Auftragsdaten)")
    with kpi_cols[3]: 
        st.metric(label="Abweichung Summen", value=auftraege_abgleich.shape[0] if auftraege_abgleich is not None else 0, delta=get_delta("count_abweichung_summen"), delta_color="inverse", help="Anzahl der Aufträge mit Abweichungen in den Summen (Auftragssumme = Summe der Positionen)")
        st.caption(f"Anteil: {anteil_summe:.2f}% relevanter Datensätze (Auftragsdaten)")
    st.markdown("---")

    st.subheader("Fehlerverlauf im Vergleich")
    
    def prepare_trend_data(df, label, time_col="CRMEingangszeit"):
        if df is None or df.empty or time_col not in df.columns:
            return pd.DataFrame()
        
        temp = df.copy()
        temp[time_col] = pd.to_datetime(temp[time_col], errors="coerce")
        temp = temp.dropna(subset=[time_col])
        
        temp["Monat"] = temp[time_col].dt.to_period("M").dt.to_timestamp()
        
        aggregated = temp.groupby("Monat").size().reset_index(name="Anzahl")
        aggregated["Kategorie"] = label
        return aggregated

    df_trend_1 = prepare_trend_data(zeitwert_error_df, "Zeitwert Fehler")
    df_trend_2 = prepare_trend_data(above_50k_df, "Aufträge > 50k")
    df_trend_3 = prepare_trend_data(auftraege_abgleich, "Abweichung Summen")

    combined_trend = pd.concat([df_trend_1, df_trend_2, df_trend_3], ignore_index=True)

    if not combined_trend.empty:
        min_date = combined_trend["Monat"].min().date()
        max_date = combined_trend["Monat"].max().date()
        
        all_kategorien = combined_trend["Kategorie"].unique()

        col_ctrl1, col_ctrl2 = st.columns([1, 1])

        with col_ctrl1:
            if min_date != max_date:
                selected_range = st.slider(
                    "Zeitraum eingrenzen:",
                    min_value=min_date,
                    max_value=max_date,
                    value=(min_date, max_date),
                    format="MMM YYYY",
                    key="p2_trend_slider"
                )
            else:
                selected_range = (min_date, max_date)

        with col_ctrl2:
            selected_metrics = st.multiselect(
                "Metriken auswählen:",
                options=all_kategorien,
                default=all_kategorien,
                key="p2_trend_multiselect"
            )
            
        mask_date = (combined_trend["Monat"].dt.date >= selected_range[0]) & (combined_trend["Monat"].dt.date <= selected_range[1])
        mask_cat = combined_trend["Kategorie"].isin(selected_metrics)
        
        chart_data = combined_trend.loc[mask_date & mask_cat]

        if not chart_data.empty:
            line_chart = alt.Chart(chart_data).mark_line(point=True).encode(
                x=alt.X("Monat:T", title="Monat", axis=alt.Axis(format="%b %Y")),
                y=alt.Y("Anzahl:Q", title="Anzahl Vorfälle"),
                color=alt.Color("Kategorie:N", title="Metrik", scale=alt.Scale(scheme="category10")),
                tooltip=[
                    alt.Tooltip("Monat:T", format="%B %Y"),
                    alt.Tooltip("Kategorie:N"),
                    alt.Tooltip("Anzahl:Q")
                ]
            ).properties(
                height=350,
                width="container"
            ).interactive()

            st.altair_chart(line_chart, width="stretch")
        else:
            st.warning("Keine Daten für die aktuelle Auswahl verfügbar.")

    else:
        st.info("Nicht genügend Zeitdaten für ein Verlaufsdiagramm vorhanden.")

    st.markdown("---")

    # --- CHARTS ---
    chart_col1, chart_col2 = st.columns(2)

# Welche Spalten sollten noch rein um die Daten sinnvoll prüfen zu können? Aktuell kein Spaltenname da Series
    with chart_col1:
        st.subheader("Die inkorrekten Zeitwerte:")
        st.caption("Auflistung aller Aufträge mit inkorrekten Zeitwerten in der Zeitwert-Spalte.")
        st.dataframe(zeitwert_error_df)
        csv_zeitwert = zeitwert_error_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="Details als CSV herunterladen",
            data=csv_zeitwert,
            file_name="zeitwert_fehler_details.csv",
            mime="text/csv",
        )


    with chart_col2:
        st.subheader("Abweichungen Auftragssumme vs. Positionssummen:")
        st.caption("Auflistung aller Aufträge, bei denen die Auftragssumme nicht mit der Summe der Positionen übereinstimmt.")
        st.dataframe(auftraege_abgleich)
        csv_abweichungen = auftraege_abgleich.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Details als CSV herunterladen",
            data=csv_abweichungen,
            file_name="auftragssumme_abweichungen_details.csv",
            mime="text/csv",
        )

    st.subheader("Aufträge über 50.000€:")
    st.caption("Auflistung aller Aufträge mit einem Wert über 50.000€.")
    st.dataframe(above_50k_df)
    csv_above_50k = above_50k_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="Details als CSV herunterladen",
        data=csv_above_50k,
        file_name="auftraege_ueber_50k_details.csv",
        mime="text/csv",
    )