import streamlit as st
import pandas as pd
import altair as alt

def show_page(metrics_df1, metrics_df2, metrics_combined, comparison_df=None, issues_df=None):

    # Helperfunction to get delta from comparison_df
    def get_delta(metric_name):
        if comparison_df is None or comparison_df.empty:
            return None
        
        row = comparison_df[comparison_df['Metric'] == metric_name]
        
        if not row.empty:
            val = row.iloc[0]['Percent_Change']
            return f"{val:+.2f}%"
        return None


    plausi_list_df1 = metrics_df1.get("plausi_forderung_einigung_list", pd.Series(dtype=float))
    plausi_count_df1 = metrics_df1.get("plausi_forderung_einigung_count", 0)
    plausi_avg_df1 = metrics_df1.get("plausi_forderung_einigung_avg_diff", 0.0)
    plausi_outliers_df1 = metrics_df1.get("plausi_outliers")

    plausi_list_df2 = metrics_df2.get("plausi_forderung_einigung_list", pd.Series(dtype=float))
    plausi_count_df2 = metrics_df2.get("plausi_forderung_einigung_count", 0)
    plausi_avg_df2 = metrics_df2.get("plausi_forderung_einigung_avg_diff", 0.0)
    plausi_outliers_df2 = metrics_df2.get("plausi_outliers")

    discount_errors = metrics_df2.get("discount_check_errors", 0)
    disc_stats = metrics_df2.get("discount_stats")
    disc_details = metrics_df2.get("discount_details")

    proforma_df = metrics_df1.get("proforma_belege_df")
    proforma_count = metrics_df1.get("proforma_belege_count", 0)

    fn_count_df1 = metrics_df1.get("false_negative", 0)
    fn_stats_df1 = metrics_df1.get("false_negative_stats")
    fn_details_df1 = metrics_df1.get("false_negative_details")

    fn_count_df2 = metrics_df2.get("false_negative", 0)
    fn_stats_df2 = metrics_df2.get("false_negative_stats")
    fn_details_df2 = metrics_df2.get("false_negative_details")

    total_df1 = metrics_df1.get("row_count", 0)
    total_df2 = metrics_df2.get("row_count", 0)

    plausi_issue = issues_df["plausi_issues"] if issues_df is not None else 0
    anteil_plausi_issues = (plausi_issue / (total_df1 + total_df2)) * 100 if (total_df1 + total_df2) > 0 else 0

    st.markdown("### Plausibilitäts-Checks & Logikfehler")
    kpi_cols = st.columns(1)
    with kpi_cols[0]:
        st.metric(
            label="Plausibilitäts-Auffälligkeiten",
            value=f"{plausi_issue:,}".replace(",", "."),
            delta=get_delta("plausi_issues"),
            delta_color="inverse",
            help="Textuelle Fehler und Warnings im Datensatz"
        )
        st.caption(f"Anteil: {anteil_plausi_issues:.2f}% an beiden Datensätzen")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Logikfehler: Forderung < Einigung",
        "Rabatt/Vorzeichen",
        "Proforma-Belege",
        "Validierung der Vorzeichenlogik (Auftrag)",
        "Validierung der Vorzeichenlogik (Position)",
    ])

    with tab1:
        st.subheader("Logikfehler: Forderung < Einigung")
        st.caption("Fälle, in denen Forderung_Netto kleiner als Einigung_Netto ist")

        dataset_choice = st.radio("Datensatz wählen", ["Auftragsdaten (df1)", "Positionsdaten (df2)"], horizontal=True)

        if "Auftragsdaten" in dataset_choice:
            count_val = plausi_count_df1
            avg_val = plausi_avg_df1
            diff_list = plausi_list_df1
            total_rows = total_df1
            outliers_view = plausi_outliers_df1
            id_col = "KvaRechnung_ID"
            file_suffix = "auftraege"
        else:
            count_val = plausi_count_df2
            avg_val = plausi_avg_df2
            diff_list = plausi_list_df2
            total_rows = total_df2
            outliers_view = plausi_outliers_df2
            id_col = "Position_ID"
            file_suffix = "positionen"

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Anzahl Fälle", value=f"{count_val:,}".replace(",", "."), help="Anzahl der Fälle, in denen Forderung_Netto < Einigung_Netto")
        c2.metric("Quote", f"{(count_val / total_rows) * 100:.2f}%" if total_rows else "NA", help="Anteil der fehlerhaften Fälle am gesamten Datensatz")
        c3.metric("Ø Abweichung", f"{avg_val:,.2f} €", help="Durchschnittliche Differenz zwischen Forderung_Netto und Einigung_Netto bei fehlerhaften Fällen")

        # Berechnung P95 für Chart-Skalierung
        if not diff_list.empty:
            p95 = diff_list.quantile(0.95)
        else:
            p95 = 0

        c4.metric("P95", f"{p95:,.2f} €", help="95. Perzentil der Differenzen zwischen Forderung_Netto und Einigung_Netto bei fehlerhaften Fällen")

        c_chart1, c_chart2 = st.columns(2)

        # Chart 1: Histogramm
        with c_chart1:
            if not diff_list.empty:
                hist_data = pd.DataFrame({"Diff": diff_list})
                # Filter für bessere Ansicht im Histogramm (bis P95)
                hist = alt.Chart(hist_data[hist_data["Diff"] <= (p95 * 1.5 if p95 > 0 else 100)]).mark_bar().encode(
                    x=alt.X("Diff:Q", bin=True, title="Differenz"), 
                    y=alt.Y("count()", title="Anzahl"),
                ).properties(height=300, title="Verteilung")
                st.altair_chart(hist, width="stretch")
            else:
                st.info("Keine Daten für Histogramm.")

        # Chart 2: Top Ausreißer
        with c_chart2:
            if not outliers_view.empty:
                # Top 10 Logik für Chart
                top_10 = outliers_view[outliers_view["Diff"] > p95].head(10) if p95 > 0 else outliers_view.head(10)
                
                if not top_10.empty:
                    bar = alt.Chart(top_10).mark_bar(color="#E4572E").encode(
                        x="Diff:Q", y=alt.Y(f"{id_col}:N", sort="-x")
                    ).properties(height=300, title="Top 10 Ausreißer (> P95)")
                    st.altair_chart(bar, width="stretch")
                else:
                    st.info("Keine extremen Ausreißer für Grafik vorhanden.")
            else:
                st.caption("Keine Daten vorhanden.")

        st.markdown("---")
        if not outliers_view.empty:
            with st.expander(f"Details anzeigen ({dataset_choice})"):
                st.markdown(f"**Gefundene Einträge: {len(outliers_view)}**")
                st.dataframe(outliers_view, width="stretch")

                csv_plausi = outliers_view.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="Details als CSV herunterladen",
                    data=csv_plausi,
                    file_name=f"plausibilitaet_einigung_forderung_{file_suffix}.csv",
                    mime="text/csv",
                )
        else:
            st.success("Keine Auffälligkeiten in diesem Datensatz gefunden.")

    with tab2:
        st.subheader("Rabatt-Logik & Vorzeichen")
        st.caption("Fälle, in denen Rabatte unplausibel sind. (Rabatte werden anhand von Keywords erkannt) Vorzeichen-Checks nur bei Einigung_netto.")
        c1, c2 = st.columns(2)
        c1.metric("Unplausible Positionen", value=f"{discount_errors:,}".replace(",", "."), delta=get_delta("count_discount_logic_errors"), delta_color="inverse", help="Anzahl der Positionen mit unplausiblen Rabatten")

        c2.metric("Anteil an Positionen", f"{(discount_errors / total_df2) * 100:.2f}%" if total_df2 else "NA", help="Prozentualer Anteil der unplausiblen Positionen am gesamten Datensatz")

        if not disc_stats.empty:
            bar = alt.Chart(disc_stats).mark_bar(color="#E4572E").encode(
                x=alt.X("Anzahl:Q", axis=alt.Axis(tickMinStep=1, format='d')),
                y=alt.Y("Bezeichnung:N", sort="-x"),
                tooltip=["Bezeichnung", "Anzahl"]
            ).properties(height=400, title="Top Fehlerquellen")
            st.altair_chart(bar, width="stretch")

        if not disc_details.empty:
            with st.expander("Details anzeigen"):
                st.markdown(f"**Gefundene Einträge: {len(disc_details)}**")
                st.dataframe(disc_details, width="stretch")

                csv_disc = disc_details.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="Details als CSV herunterladen",
                    data=csv_disc,
                    file_name="rabatt_fehler_details.csv",
                    mime="text/csv",
                )

    with tab3:
            st.subheader("Erkannte Proforma-Belege")
            st.caption("Aufträge, die als Proforma-Belege identifiziert wurden. (Performa-Beleg = Aufträge mit Einigung_Netto zwischen 0,01 und 1 €.)")
            c1, c2 = st.columns(2)
            c1.metric("Anzahl Belege", value=f"{proforma_count:,}".replace(",", "."), delta=get_delta("count_proforma_receipts"), delta_color="inverse", help="Anzahl der als Proforma-Belege identifizierten Aufträge")
            c2.metric("Anteil an Aufträgen", f"{(proforma_count / total_df1) * 100:.2f}%" if total_df1 else "NA", help="Prozentualer Anteil der Proforma-Belege am gesamten Auftragsdatensatz")

            if not proforma_df.empty:
                if "CRMEingangszeit" in proforma_df.columns:
                    line = alt.Chart(proforma_df).mark_line(point=True).encode(
                        x=alt.X("yearmonth(CRMEingangszeit):T", title="Zeitraum"),
                        y=alt.Y("count()", title="Anzahl", axis=alt.Axis(tickMinStep=1, format='d'))
                    ).properties(height=300)
                    st.altair_chart(line, width="stretch")

                with st.expander("Details anzeigen"):
                    st.markdown(f"**Gefundene Einträge: {len(proforma_df)}**")
                    st.dataframe(proforma_df, width="stretch")
                    csv_proforma = proforma_df.to_csv(index=False).encode('utf-8')

                    st.download_button(
                        label="Details als CSV herunterladen",
                        data=csv_proforma,
                        file_name="proforma_belege.csv",
                        mime="text/csv",
                    )

    with tab4:
        st.subheader("Validierung der Vorzeichenlogik in Auftragsdaten")
        st.caption("Aufträge mit inkonsistenten Vorzeichen bei Forderung, Empfehlung und Einigung.")
        c1, c2, c3 = st.columns(3)
        c1.metric("Fehlerhafte Aufträge", value=f"{fn_count_df1:,}".replace(",", "."), delta=get_delta("count_false_negative_df"), delta_color="inverse", help="Anzahl der Aufträge mit inkonsistenten Vorzeichen bei Forderung, Einigung und Auftragssumme")
        c2.metric("Anteil an Aufträgen", f"{(fn_count_df1 / total_df1) * 100:.2f}%" if total_df1 else "NA", help="Prozentualer Anteil der fehlerhaften Aufträge am gesamten Auftragsdatensatz")
        c3.metric("Gesamt Aufträge", value=f"{total_df1:,}".replace(",", "."), help="Gesamtanzahl der Aufträge im Datensatz")

        if not fn_stats_df1.empty:
            bar = alt.Chart(fn_stats_df1).mark_bar().encode(
                x=alt.X("Fehler:Q", axis=alt.Axis(tickMinStep=1, format='d')),
                y=alt.Y("Spalte:N", sort="-x"),
                tooltip=["Spalte", "Fehler"]
            ).properties(height=300, title="Fehlerverteilung")
            st.altair_chart(bar, width="stretch")

        if not fn_details_df1.empty:
            with st.expander("Details anzeigen"):
                st.markdown(f"**Gefundene Einträge: {len(fn_details_df1)}**")
                st.dataframe(fn_details_df1, width="stretch")
                csv_data = fn_details_df1.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="Details als CSV herunterladen",
                    data=csv_data,
                    file_name="tripel_fehler_details.csv",
                    mime="text/csv",
                )

    with tab5:
        st.subheader("Validierung der Vorzeichenlogik in Positionsdaten")
        st.caption("Positionen mit inkonsistenten Vorzeichen bei Forderung, Einigung, Positionssumme und Menge.")
        c1, c2, c3 = st.columns(3)
        c1.metric("Inkonsistente Positionen", value=f"{fn_count_df2:,}".replace(",", "."), delta=get_delta("count_false_negative_df2"), delta_color="inverse", help="Anzahl der Positionen mit inkonsistenten Vorzeichen bei Forderung, Einigung und Positionssumme")
        c2.metric("Anteil an Positionen", f"{(fn_count_df2 / total_df2) * 100:.2f}%" if total_df2 else "NA", help="Prozentualer Anteil der fehlerhaften Positionen am gesamten Positionsdatensatz")
        c3.metric("Gesamt Positionen", value=f"{total_df2:,}".replace(",", "."), help="Gesamtanzahl der Positionen im Datensatz")

        if not fn_stats_df2.empty:
            bar = alt.Chart(fn_stats_df2).mark_bar().encode(
                x="Anzahl:Q",
                y=alt.Y("Kategorie:N", sort="-x"),
                tooltip=["Kategorie", "Anzahl"]
            ).properties(height=300, title="Fehlerkategorien")
            st.altair_chart(bar, width="stretch")

        if not fn_details_df2.empty:
            with st.expander("Details anzeigen"):
                st.markdown(f"**Gefundene Einträge: {len(fn_details_df2)}**")
                st.dataframe(fn_details_df2, width="stretch")
                csv_data_2 = fn_details_df2.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="Details als CSV herunterladen",
                    data=csv_data_2,
                    file_name="konsistenz_fehler_details.csv",
                    mime="text/csv",
                )

    st.markdown("---")