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


    # DATEN LADEN
    df_outlier = metrics_df1.get("handwerker_gewerke_outlier")
    df_semantic = metrics_df1.get("mismatched_entries")
    test_data_df = metrics_df1.get("test_data_df", pd.DataFrame()) 
    
    kundengruppe_containing_test = metrics_df1.get("test_kundengruppen_anzahl")
    row_count = metrics_df1.get("row_count") 
    row_count_df2 = metrics_df2.get("row_count")
    text_issues = issues_df["text_issues"]
    anteil_text_issues = (text_issues / (row_count + row_count_df2)) * 100
    anteil_testdaten = (kundengruppe_containing_test / row_count * 100)

    # outlier KPI
    outlier_count = len(df_outlier[df_outlier['is_outlier'] == True])
    outlier_share = (outlier_count / row_count * 100)

    # KPI HEADER
    kpi_cols = st.columns(3)
    with kpi_cols[0]:
        st.metric(
            label="Textuelle Auffälligkeiten",
            value=f"{text_issues:,}".replace(",", "."),
            delta=get_delta("text_issues"), 
            delta_color="inverse",
            help="Textuelle Fehler und Warnings im Datensatz"
        )
        st.caption(f"Anteil: {anteil_text_issues:.2f}% an beiden Datensätzen")
    with kpi_cols[1]: 
        st.metric(
            label="Testdatensätze in Kundengruppe",
            value=f"{kundengruppe_containing_test:,}".replace(",", "."),
            delta=get_delta("count_test_data_rows"), 
            delta_color="inverse",
            help="Anzahl der Aufträge, die als Testdatensätze identifiziert wurden"
        )
        st.caption(f"Anteil: {anteil_testdaten:.2f}% der Auftragsdaten")

    with kpi_cols[2]:
        st.metric(
            label="Auffällige Gewerk-Zuordnungen",
            value=f"{outlier_count:,}".replace(",", "."),
            delta=get_delta("count_handwerker_outliers"), 
            delta_color="inverse",
            help="Anzahl der Aufträge mit auffälligen Handwerker-Gewerk Zuordnungen"
        )
        st.caption(f"Anteil: {outlier_share:.2f}% der Auftragsdaten")
    


    st.markdown("---")

    # ZEITVERLAUF DIAGRAMM (MIT RAW DATA VIEW)
    st.subheader("Fehlerverlauf im Vergleich:")
    st.caption("Dieses Diagramm zeigt den Verlauf der ausgewählten Fehlerkategorien über den gewählten Zeitraum. Aktuell können nur Testdatensätze visualisiert werden.")

    def prepare_trend_data(df, label, time_col="CRMEingangszeit"):
        """Bereitet DataFrame für das Zeitreihendiagramm (Aggregation) vor."""
        if df is None or df.empty or time_col not in df.columns:
            return pd.DataFrame()
        
        temp = df.copy()
        temp[time_col] = pd.to_datetime(temp[time_col], errors="coerce")
        temp = temp.dropna(subset=[time_col])
        
        temp["Monat"] = temp[time_col].dt.to_period("M").dt.to_timestamp()
        
        aggregated = temp.groupby("Monat").size().reset_index(name="Anzahl")
        aggregated["Kategorie"] = label
        return aggregated

    # Daten für Chart vorbereiten (Aggregiert)
    df_trend_test = prepare_trend_data(test_data_df, "Testdatensätze")
    
    combined_trend = pd.concat([df_trend_test], ignore_index=True)

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
                    key="p3_trend_slider"
                )
            else:
                selected_range = (min_date, max_date)

        with col_ctrl2:
            selected_metrics = st.multiselect(
                "Metriken auswählen:",
                options=all_kategorien,
                default=all_kategorien,
                key="p3_trend_multiselect"
            )

        # View Toggle
        view_mode_trend = st.radio(
            "Ansicht (Zeitverlauf):",
            ["Grafische Auswertung", "Detail-Tabelle"],
            horizontal=True,
            label_visibility="collapsed",
            key="p3_trend_view_toggle"
        )
        
        if view_mode_trend == "Grafische Auswertung":
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
                st.warning("Keine Chart-Daten für die aktuelle Auswahl verfügbar.")
        
        else:
            
            raw_frames = []

            if "Testdatensätze" in selected_metrics and not test_data_df.empty:
                temp_raw = test_data_df.copy()
                
                temp_col = "CRMEingangszeit"
                if temp_col in temp_raw.columns:
                    temp_raw[temp_col] = pd.to_datetime(temp_raw[temp_col], errors="coerce")
                    
                    mask_raw = (temp_raw[temp_col].dt.date >= selected_range[0]) & \
                               (temp_raw[temp_col].dt.date <= selected_range[1])
                    
                    filtered_raw = temp_raw.loc[mask_raw].copy()
                    
                    filtered_raw.insert(0, "Fehlerkategorie", "Testdatensatz")
                    
                    raw_frames.append(filtered_raw)

            if raw_frames:
                final_raw_df = pd.concat(raw_frames, ignore_index=True)
                
                st.markdown(f"**Gefundene Einträge: {len(final_raw_df)}** im Zeitraum {selected_range[0].strftime('%d.%m.%Y')} bis {selected_range[1].strftime('%d.%m.%Y')}")
                
                st.dataframe(
                    final_raw_df, 
                    width="stretch", 
                    hide_index=True
                )

                csv_raw = final_raw_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Rohdaten als CSV herunterladen",
                    data=csv_raw,
                    file_name="zeitverlauf_rohdaten_text.csv",
                    mime="text/csv"
                )
            else:
                st.info("Keine Rohdaten für die gewählten Metriken im ausgewählten Zeitraum gefunden.")

    else:
        st.info("Nicht genügend Zeitdaten für ein Verlaufsdiagramm vorhanden.")

    st.markdown("---")

    # DETAIL ANALYSE (OUTLIERS)
    st.subheader("Statistische Auffälligkeiten (Handwerker vs. Gewerk)")
    st.caption("Diese Analyse identifiziert Handwerker und Gewerke, bei den auffällig viele Zuordnungsfehler auftreten. (Der Namensabgleich prüft, ob der Handwerkername auf das Gewerk hinweist)")

    tab1, tab2 = st.tabs(['Regelbasiert', 'Semantisch'])

    with tab1:
        if df_outlier is not None and not df_outlier.empty:

            st.caption("Wenn das angegebene Gewerk eines Handwerkers in weniger als 20% seiner gesamten Aufträge vorkommt wird dieses als Ausreißer deklariert. ")
            st.caption("In der Detail-Tabelle kann zusätzlich eingesehen werden ob ein Keyword aus einem anderen Gewerk im Namen des Handwerkers gefunden wurde als das angegebene Gewerk.")

            view_mode_outlier = st.radio(
                "Darstellung (Auffälligkeiten):",
                ["Grafische Auswertung", "Detail-Tabelle"],
                horizontal=True,
                label_visibility="collapsed",
                key="p3_outlier_view_toggle"
            )

            if view_mode_outlier == "Grafische Auswertung":

                st.markdown("#### Fehlerschwerpunkte nach Gewerk")
                grouped_gewerk = df_outlier['Gewerk_Name'].value_counts().reset_index()
                grouped_gewerk.columns = ['Gewerk', 'Anzahl']

                chart_gewerk = alt.Chart(grouped_gewerk.head(10)).mark_bar().encode(
                    x=alt.X('Anzahl:Q', title="Anzahl Auffälligkeiten"),
                    y=alt.Y('Gewerk:N', sort='-x', title="Gewerk"),
                    tooltip=['Gewerk', 'Anzahl'],
                    color=alt.value("#E4572E")
                ).properties(height=280)
                st.altair_chart(chart_gewerk, width="stretch")

                st.markdown("---")

                st.markdown("#### Top-Verursacher")

                df_hw = df_outlier.copy()

                grouped_hw = df_hw.groupby('Handwerker_Name', observed=True)['count'].sum().reset_index()
                grouped_hw.columns = ['Handwerker', 'Summe_Fehler']

                grouped_hw = grouped_hw.sort_values('Summe_Fehler', ascending=False).head(10)

                chart_hw = alt.Chart(grouped_hw).mark_bar().encode(
                    x=alt.X('Summe_Fehler:Q', title="Summe potenziell fehlerhafter Aufträge"),
                    y=alt.Y('Handwerker:N', sort='-x', title="Handwerker"),
                    tooltip=['Handwerker', 'Summe_Fehler'],
                    color=alt.value("#442D7B")
                ).properties(height=280)
                st.altair_chart(chart_hw, width="stretch")

            else:
                # Tabellenansicht Outlier
                df_display = df_outlier.copy()

                if 'ratio' in df_display.columns:
                    df_display['ratio'] = (df_display['ratio'] * 100).round(2).astype(str) + '%'

                rename_map = {
                    "Handwerker_Name": "Handwerker",
                    "Gewerk_Name": "Gewerk (Auftrag)",
                    "count": "Anzahl Aufträge",
                    "ratio": "Anteil am Gesamtvolumen",
                    "Check_Result": "Namensabgleich"
                }

                cols_to_show = [c for c in rename_map.keys() if c in df_display.columns]

                st.dataframe(
                    df_display[cols_to_show].rename(columns=rename_map),
                    width="stretch",
                    hide_index=True
                )
                
                # Download Button für die Outlier Tabelle
                csv_outlier = df_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Tabelle als CSV herunterladen",
                    data=csv_outlier,
                    file_name="handwerker_outliers.csv",
                    mime="text/csv"
                )

        else:
            st.success("Keine statistischen Auffälligkeiten in den Daten gefunden.")

    with tab2:
        if df_outlier is not None and not df_outlier.empty:

            st.caption("Es wird ein semantischer Vergleich des Gewerks mit dem Handwerkernamen durchgeführt. Ein zu starker Unterschied wird als fehlerhaft ausgegeben.")

            view_mode_outlier = st.radio(
                "Darstellung (Auffälligkeiten):",
                ["Grafische Auswertung", "Detail-Tabelle"],
                horizontal=True,
                label_visibility="collapsed",
                key="p3_semantic_view_toggle"
            )

            if view_mode_outlier == "Grafische Auswertung":

                st.markdown("#### Fehlerschwerpunkte nach Gewerk")
                grouped_gewerk = df_semantic['Gewerk_Name'].value_counts().reset_index()
                grouped_gewerk.columns = ['Gewerk', 'Anzahl']

                chart_gewerk = alt.Chart(grouped_gewerk.head(10)).mark_bar().encode(
                    x=alt.X('Anzahl:Q', title="Anzahl Auffälligkeiten"),
                    y=alt.Y('Gewerk:N', sort='-x', title="Gewerk"),
                    tooltip=['Gewerk', 'Anzahl'],
                    color=alt.value("#E4572E")
                ).properties(height=280)
                st.altair_chart(chart_gewerk, width="stretch")

                st.markdown("---")

                st.markdown("#### Top-Verursacher")

                df_sem = df_semantic.copy()

                grouped_hw = df_sem['Handwerker_Name'].value_counts().reset_index()
                grouped_hw.columns = ['Handwerker', 'Summe_Fehler']

                grouped_hw = grouped_hw.sort_values('Summe_Fehler', ascending=False).head(10)

                chart_hw = alt.Chart(grouped_hw).mark_bar().encode(
                    x=alt.X('Summe_Fehler:Q', title="Summe potenziell fehlerhafter Aufträge"),
                    y=alt.Y('Handwerker:N', sort='-x', title="Handwerker"),
                    tooltip=['Handwerker', 'Summe_Fehler'],
                    color=alt.value("#442D7B")
                ).properties(height=280)
                st.altair_chart(chart_hw, width="stretch")

            else:
                # Tabellenansicht Outlier
                df_display = df_semantic[['Gewerk_Name', 'Handwerker_Name', 'Similarity_Score']].copy()

                rename_map = {
                    "Handwerker_Name": "Handwerker",
                    "Gewerk_Name": "Gewerk (Auftrag)",
                    "Similarity_Score": "Ähnlichkeit"
                }

                cols_to_show = [c for c in rename_map.keys() if c in df_display.columns]

                st.dataframe(
                    df_display[cols_to_show].rename(columns=rename_map),
                    width="stretch",
                    hide_index=True
                )
                
                # Download Button für die Outlier Tabelle
                csv_semantic = df_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Tabelle als CSV herunterladen",
                    data=csv_semantic,
                    file_name="handwerker_semantic.csv",
                    mime="text/csv"
                )

        else:
            st.success("Keine statistischen Auffälligkeiten in den Daten gefunden.")