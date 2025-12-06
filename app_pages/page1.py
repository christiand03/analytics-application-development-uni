import streamlit as st
import pandas as pd
import altair as alt
import metrics as mt

def show_page(df, df2, metrics_df1, metrics_df2, metrics_combined):

    # --- KPI-BEREICH (6 Kacheln) ---
    kpi_cols = st.columns(6)

    row_count_df1 = metrics_df1.get("row_count", len(df))
    row_count_df2 = metrics_df2.get("row_count", len(df2))
    null_rows_df1 = metrics_df1.get("null_ratio_rows", mt.ratio_null_values_rows(df))
    null_rows_df2 = metrics_df2.get("null_ratio_rows", mt.ratio_null_values_rows(df2))
    proforma_count = metrics_df1.get("proforma_belege_count", 0)

    kva_unique = metrics_combined.get("kvarechnung_id_is_unique", None)
    pos_unique = metrics_combined.get("position_id_is_unique", None)

    with kpi_cols[0]:
        st.metric(label="Aufträge (df)", value=f"{row_count_df1:,}".replace(",", "."), help="Anzahl Zeilen in Auftragsdaten (df).")
    with kpi_cols[1]:
        st.metric(label="Positionen (df2)", value=f"{row_count_df2:,}".replace(",", "."), help="Anzahl Zeilen in Positionsdaten (df2).")
    with kpi_cols[2]:
        st.metric(label="Fehlerquoten (df) [%]", value=f"{null_rows_df1:.2f}%", help="Anteil der Zeilen mit mindestens einem Null-/Fehlerwert in df.")
    with kpi_cols[3]:
        st.metric(label="Fehlerquoten (df2) [%]", value=f"{null_rows_df2:.2f}%", help="Anteil der Zeilen mit mindestens einem Null-/Fehlerwert in df2.")
    with kpi_cols[4]:
        st.metric(label="Proforma‑Belege", value=f"{proforma_count:,}".replace(",", "."), help="Anzahl Aufträge mit Einigung_Netto zwischen 0,01 und 1 €.")
    with kpi_cols[5]:
        uniq_text = (
            "OK" if (kva_unique is True and pos_unique is True) else
            ("KVA ok, Pos. nicht" if (kva_unique is True and pos_unique is False) else
             ("KVA nicht, Pos. ok" if (kva_unique is False and pos_unique is True) else
              ("n/v" if (kva_unique is None or pos_unique is None) else "beide nicht")))
        )
        st.metric(label="Eindeutigkeit IDs", value=uniq_text, help="Prüft Einzigartigkeit von KvaRechnung_ID (df) und Position_ID (df2).")

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # CHART-BEREICH
    chart_col1, chart_col2 = st.columns(2)

    # Chart 1: Nullwerte je Spalte (Top N) aus df
    with chart_col1:
        st.subheader("Nullwerte je Spalte (Top N)")

        null_ratio_cols = metrics_df1.get("null_ratio_cols", {})
        if isinstance(null_ratio_cols, dict) and null_ratio_cols:
            n = st.slider("Anzahl Spalten (Top N)", min_value=5, max_value=min(30, len(null_ratio_cols)), value=min(10, len(null_ratio_cols)), key="p1_topn")
            null_df = (
                pd.DataFrame(list(null_ratio_cols.items()), columns=["Spalte", "Nullquote_%"]).sort_values("Nullquote_%", ascending=False).head(n)
            )

            bar = (
                alt.Chart(null_df)
                .mark_bar()
                .encode(
                    x=alt.X("Nullquote_%:Q", title="Nullquote [%]"),
                    y=alt.Y("Spalte:N", sort='-x', title="Spalte"),
                    tooltip=["Spalte", alt.Tooltip("Nullquote_%:Q", format=".2f")]
                )
                .properties(height=28 * len(null_df), width="container")
            )
            st.altair_chart(bar, width="stretch")
        else:
            st.info("Keine Nullwert-Informationen verfügbar.")

    # Chart 2: Fehlerhäufigkeit nach Wochentag und Stunde (Heatmap)
    with chart_col2:
        st.subheader("Fehlerquote nach Wochentag und Stunde")
        err_df = metrics_df1.get("error_frequency_weekday_hour", None)
        if isinstance(err_df, pd.DataFrame) and not err_df.empty:
            weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            if "weekday" in err_df.columns:
                err_df["weekday"] = pd.Categorical(err_df["weekday"], categories=weekday_order, ordered=True)

            heat = (
                alt.Chart(err_df)
                .mark_rect()
                .encode(
                    x=alt.X("hour:O", title="Stunde"),
                    y=alt.Y("weekday:O", sort=weekday_order, title="Wochentag"),
                    color=alt.Color("error_rate:Q", title="Fehlerquote [%]", scale=alt.Scale(scheme="reds")),
                    tooltip=[
                        alt.Tooltip("weekday:N", title="Wochentag"),
                        alt.Tooltip("hour:Q", title="Stunde"),
                        alt.Tooltip("total_rows:Q", title="Anzahl Aufträge"),
                        alt.Tooltip("error_rows:Q", title="Fehlerfälle"),
                        alt.Tooltip("error_rate:Q", title="Fehlerquote", format=".2f")
                    ]
                )
                .properties(height=240, width="container")
            )
            st.altair_chart(heat, width="stretch")
        else:
            st.info("Keine Fehlerfrequenz-Daten verfügbar.")