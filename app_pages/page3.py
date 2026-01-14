import streamlit as st
import altair as alt


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
            label="Auffällige Gewerk-Zuordnungen",
            value=str(outlier_count),
            delta=f"{outlier_share:.2f}% der Datensätze",
            delta_color="inverse"
        )

    st.markdown("---")

    #st.subheader("Semantische Prüfung (KI-Modell)")

    st.subheader("Statistische Auffälligkeiten (Handwerker vs. Gewerk)")

    if df_outlier is not None and not df_outlier.empty:

        # Toggle für Ansicht
        view_mode = st.radio(
            "Darstellung:",
            ["Grafische Auswertung", "Detail-Tabelle"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if view_mode == "Grafische Auswertung":

            st.markdown("#### Fehlerschwerpunkte nach Gewerk")
            grouped_gewerk = df_outlier['Gewerk_Name'].value_counts().reset_index()
            grouped_gewerk.columns = ['Gewerk', 'Anzahl']

            chart_gewerk = alt.Chart(grouped_gewerk.head(10)).mark_bar().encode(
                x=alt.X('Anzahl:Q', title="Anzahl Auffälligkeiten"),
                y=alt.Y('Gewerk:N', sort='-x', title="Gewerk"),
                tooltip=['Gewerk', 'Anzahl'],
                color=alt.value("#E4572E")
            ).properties(height=280)
            st.altair_chart(chart_gewerk, use_container_width=True)

            st.markdown("---")

            st.markdown("#### Top-Verursacher (Handwerker)")

            df_hw = df_outlier.copy()

            grouped_hw = df_hw.groupby('Handwerker_Name')['count'].sum().reset_index()
            grouped_hw.columns = ['Handwerker', 'Summe_Fehler']

            grouped_hw = grouped_hw.sort_values('Summe_Fehler', ascending=False).head(10)

            chart_hw = alt.Chart(grouped_hw).mark_bar().encode(
                x=alt.X('Summe_Fehler:Q', title="Summe fehlerhafter Aufträge"),
                y=alt.Y('Handwerker:N', sort='-x', title="Handwerker"),
                tooltip=['Handwerker', 'Summe_Fehler'],
                color=alt.value("#442D7B")
            ).properties(height=280)
            st.altair_chart(chart_hw, use_container_width=True)

        else:
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
                use_container_width=True,
                hide_index=True
            )

    else:
        st.success("Keine statistischen Auffälligkeiten in den Daten gefunden.")