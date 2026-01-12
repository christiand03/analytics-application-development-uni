import streamlit as st
import pandas as pd
import altair as alt

def show_page(metrics_df1, metrics_df2, metrics_combined):
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

    st.markdown("### Plausibilitäts-Checks & Logikfehler")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Einigung > Forderung",
        "Rabatt/Vorzeichen",
        "Proforma-Belege",
        "Tripel-Vorzeichen (Auftrag)",
        "Konsistenz (Positionen)"
    ])

    with tab1:
        st.subheader("Einigung > Forderung")
        st.caption("Fälle, in denen Einigung_Netto größer als Forderung_Netto ist")

        dataset_choice = st.radio("Datensatz wählen", ["Auftragsdaten (df1)", "Positionsdaten (df2)"], horizontal=True)

        if "Auftragsdaten" in dataset_choice:
            count_val = plausi_count_df1
            avg_val = plausi_avg_df1
            diff_list = plausi_list_df1
            total_rows = total_df1
            outliers_view = plausi_outliers_df1
            id_col = "KvaRechnung_ID"
        else:
            count_val = plausi_count_df2
            avg_val = plausi_avg_df2
            diff_list = plausi_list_df2
            total_rows = total_df2
            outliers_view = plausi_outliers_df2
            id_col = "Position_ID"

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Anzahl Fälle", count_val)
        c2.metric("Quote", f"{(count_val / total_rows) * 100:.2f}%" if total_rows else "NA")
        c3.metric("Ø Abweichung", f"{avg_val:,.2f} €")

        p95 = diff_list.quantile(0.95)
        c4.metric("P95", f"{p95:,.2f} €")

        c_chart1, c_chart2 = st.columns(2)

        # Chart 1: Histogramm
        with c_chart1:
            hist_data = pd.DataFrame({"Diff": diff_list})
            hist = alt.Chart(hist_data[hist_data["Diff"] <= p95]).mark_bar().encode(
                x=alt.X("Diff:Q", bin=True, title="Differenz"), y="count()"
            ).properties(height=300, title="Verteilung")
            st.altair_chart(hist, use_container_width=True)

        with c_chart2:
            if not outliers_view.empty:
                top_10 = outliers_view[outliers_view["Diff"] > p95].head(10)
                if not top_10.empty:
                    bar = alt.Chart(top_10).mark_bar(color="#E4572E").encode(
                        x="Diff:Q", y=alt.Y(f"{id_col}:N", sort="-x")
                    ).properties(height=300, title="Top 10 Ausreißer (> P95)")
                    st.altair_chart(bar, use_container_width=True)
                else:
                    st.info("Keine extremen Ausreißer.")
            else:
                if "Positionsdaten" in dataset_choice:
                    st.caption("Detail-Diagramm für Positionsdaten nicht verfügbar.")

    with tab2:
        st.subheader("Rabatt-Logik & Vorzeichen")
        c1, c2 = st.columns(2)
        c1.metric("Unplausible Positionen", discount_errors)

        c2.metric("Anteil an Positionen", f"{(discount_errors / total_df2) * 100:.2f}%" if total_df2 else "NA")

        if not disc_stats.empty:
            bar = alt.Chart(disc_stats).mark_bar(color="#E4572E").encode(
                x="Anzahl:Q",
                y=alt.Y("Bezeichnung:N", sort="-x"),
                tooltip=["Bezeichnung", "Anzahl"]
            ).properties(height=400, title="Top Fehlerquellen")
            st.altair_chart(bar, use_container_width=True)

        if not disc_details.empty:
            with st.expander("Details anzeigen"):
                st.dataframe(disc_details, use_container_width=True)

    with tab3:
        st.subheader("Erkannte Proforma-Belege")

        c1, c2 = st.columns(2)
        c1.metric("Anzahl Belege", proforma_count)
        c2.metric("Anteil an Aufträgen", f"{(proforma_count / total_df1) * 100:.2f}%" if total_df1 else "NA")

        if not proforma_df.empty:
            if "CRMEingangszeit" in proforma_df.columns:
                line = alt.Chart(proforma_df).mark_line().encode(
                    x="yearmonth(CRMEingangszeit):T", y="count()"
                ).properties(height=300)
                st.altair_chart(line, use_container_width=True)
            # Hier stand schon "Details anzeigen", aber in deinem Tab 3 Snippet war kein Expander
            with st.expander("Details anzeigen"):
                st.dataframe(proforma_df, use_container_width=True)

    with tab4:
        st.subheader("Tripel-Vorzeichen Check")

        c1, c2, c3 = st.columns(3)
        c1.metric("Fehlerhafte Aufträge", fn_count_df1)
        c2.metric("Anteil an Aufträgen", f"{(fn_count_df1 / total_df1) * 100:.2f}%" if total_df1 else "NA")
        c3.metric("Gesamt Aufträge", total_df1)

        if not fn_stats_df1.empty:
            bar = alt.Chart(fn_stats_df1).mark_bar().encode(
                x="Fehler:Q",
                y=alt.Y("Spalte:N", sort="-x"),
                tooltip=["Spalte", "Fehler"]
            ).properties(height=300, title="Fehlerverteilung")
            st.altair_chart(bar, use_container_width=True)

        if not fn_details_df1.empty:
            with st.expander("Details anzeigen"):
                st.dataframe(fn_details_df1, use_container_width=True)

    with tab5:
        st.subheader("Konsistenzprüfung")

        c1, c2, c3 = st.columns(3)
        c1.metric("Inkonsistente Positionen", fn_count_df2)
        c2.metric("Anteil an Positionen", f"{(fn_count_df2 / total_df2) * 100:.2f}%" if total_df2 else "NA")
        c3.metric("Gesamt Positionen", total_df2)

        if not fn_stats_df2.empty:
            bar = alt.Chart(fn_stats_df2).mark_bar().encode(
                x="Anzahl:Q",
                y=alt.Y("Kategorie:N", sort="-x"),
                tooltip=["Kategorie", "Anzahl"]
            ).properties(height=300, title="Fehlerkategorien")
            st.altair_chart(bar, use_container_width=True)

        if not fn_details_df2.empty:
            with st.expander("Details anzeigen"):
                st.dataframe(fn_details_df2, use_container_width=True)

    st.markdown("---")