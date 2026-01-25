import streamlit as st
import pandas as pd
import altair as alt

def show_page(metrics_df1, metrics_df2, metrics_combined, pot_df, comparison_df, issues_df):
    """This function renders page 1 of 5 of the dashboard. 
    
    Page 1 is the dashboard landing page.
    For a detailed list of diplayed info, refer to the 'Notes' section.

    Parameters
    ----------
    metrics_df1 : pandas.DataFrame
        DataFrame containing values for all metrics concerning order data only
    metrics_df2 : pandas.DataFrame
        DataFrame containing values for all metrics concerning position data only
    metrics_combined : pandas.DataFrame
        DataFrame containing values for all metrics concerning order and position data
    comparison_df : pandas.DataFrame
        DataFrame with metric value changes over time
    issues_df : bool
        DataFrame containing values for all metrics concerning potentially invalid data points
    Returns
    -------
    void        

    Notes
    -----
    This page contains the following information:
    
    - KPIs
        - total number of issues and discrepancies found
        - row counts for both order and position data sets
        - ratio of null values in both data sets
        - amount of pro forma orders
        - amount of orders without associated positions
    - Tables:
        - null values per column (top *n* columns) 
        - error frequencies aggregated over time of day & weekdays
        - trend of position count per order over time (monthly avg.)
    """
   
    # Helperfunction to get delta from comparison_df
    def get_delta(metric_name):
        if comparison_df is None or comparison_df.empty:
            return None
        
        row = comparison_df[comparison_df['Metric'] == metric_name]
        
        if not row.empty:
            val = row.iloc[0]['Percent_Change']
            return f"{val:+.2f}%"
        return None
    

    # --- KPI-BEREICH ---
    kpi_cols = st.columns(8)

    row_count_df1 = metrics_df1.get("row_count", pd.NA)
    row_count_df2 = metrics_df2.get("row_count", pd.NA)
    null_rows_df1 = metrics_df1.get("null_ratio_rows", pd.NA)
    null_rows_df2 = metrics_df2.get("null_ratio_rows", pd.NA)
    proforma_count = metrics_df1.get("proforma_belege_count", pd.NA)
    empty_orders = metrics_df1.get("empty_orders_count", 0)

    kva_unique = metrics_combined.get("kvarechnung_id_is_unique", None)
    kva_nr_land_unique = metrics_combined.get("kvarechnung_nummer_land_is_unique", None)
    pos_unique = metrics_combined.get("position_id_is_unique", None)

    total_issues = issues_df["overall_issues"] if issues_df is not None else 0

    with kpi_cols[0]:
        st.metric(label="Auffälligkeiten", value=f"{total_issues:,}".replace(",", "."), help="Alle Fehler und Warnings im Datensatz", delta=get_delta("overall_issues"), delta_color="inverse")
    with kpi_cols[1]:
        st.metric(label="Aufträge (df)", value=f"{row_count_df1:,}".replace(",", "."), help="Anzahl Zeilen in Auftragsdaten (df).", delta=get_delta("count_total_orders"), delta_color="off")
    with kpi_cols[2]:
        st.metric(label="Positionen (df2)", value=f"{row_count_df2:,}".replace(",", "."), help="Anzahl Zeilen in Positionsdaten (df2).", delta=get_delta("count_total_positions"), delta_color="off")
    with kpi_cols[3]:
        st.metric(label="Null-Anteil (Auftragsdaten)", value=f"{null_rows_df1:.2f}%", help="Anteil der Zeilen mit mindestens einem Nullwert (außer PLZ) in Auftragsdaten.", delta=get_delta("null_row_ratio_orders"), delta_color="inverse")
    with kpi_cols[4]:
        st.metric(label="Null-Anteil (Positionsdaten)", value=f"{null_rows_df2:.2f}%", help="Anteil der Zeilen mit mindestens einem Nullwert (außer Bezeichnung) in Positionsdaten.", delta=get_delta("null_row_ratio_positions"), delta_color="inverse")
    with kpi_cols[5]:
        st.metric(label="Proforma‑Belege", value=f"{proforma_count:,}".replace(",", "."), help="Anzahl Aufträge mit Einigung_Netto zwischen 0,01 und 1 €. Details sind unter Plausibilitätscheck.", delta=get_delta("count_proforma_receipts"), delta_color="inverse")
    with kpi_cols[6]:
        st.metric(label="Aufträge ohne Pos.", value=f"{empty_orders:,}".replace(",", "."), help="Anzahl der Aufträge, denen keine Positionen zugeordnet sind (PositionsAnzahl ist leer). Details sind unter Plausibilitätscheck.", delta=get_delta("count_empty_orders"), delta_color="inverse")
    with kpi_cols[7]:
        if kva_unique and kva_nr_land_unique and pos_unique:
            text = "True"
        else:
            text = "False"


        tooltip = (
            "Prüft Einzigartigkeit von:\n"
            f"- ({kva_unique}) KvaRechnung_ID (Auftragsdaten)\n"
            f"- ({kva_nr_land_unique}) KvaRechnung_Nummer pro Land (Auftragsdaten)\n"
            f"- ({pos_unique}) Position_ID (Positionsdaten)"
        )

        st.metric(
            label="Eindeutigkeit IDs",
            value=text,
            help=tooltip
        )

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)


    # CHART-BEREICH
    chart_col1, chart_col2 = st.columns(2)

    # Chart 1: Nullwerte je Spalte (Top N) aus df
    with chart_col1:
        st.subheader("Nullwerte je Spalte (Top N)")

        null_ratio_cols = metrics_df1.get("null_ratio_cols", None)

        null_df = None
        if isinstance(null_ratio_cols, dict) and len(null_ratio_cols) > 0:
            tmp = pd.DataFrame(list(null_ratio_cols.items()), columns=["Spalte", "Nullquote_%"])  # altes Format
            null_df = tmp.copy()
        elif isinstance(null_ratio_cols, pd.DataFrame) and not null_ratio_cols.empty:
            # erwartete Spalten im neuen Format: 'index' (Spaltenname) und 'null_ratio' (in %)
            df_tmp = null_ratio_cols.copy()
            # Fallback: versuche sinnvolle Spalten zu finden
            col_name_col = None
            ratio_col = None
            for cand in ["index", "column", "column_name", "Spalte"]:
                if cand in df_tmp.columns:
                    col_name_col = cand
                    break
            for cand in ["null_ratio", "Nullquote_%", "ratio", "nullratio"]:
                if cand in df_tmp.columns:
                    ratio_col = cand
                    break
            if col_name_col is None:
                # Wenn reset_index() verwendet wurde, kann der Spaltenname in der ersten Spalte ohne Namen liegen
                if df_tmp.columns.size >= 1:
                    col_name_col = df_tmp.columns[0]
            if ratio_col is None and df_tmp.columns.size >= 2:
                # Heuristik: zweite Spalte nehmen
                ratio_col = df_tmp.columns[1]

            if col_name_col is not None and ratio_col is not None:
                null_df = df_tmp[[col_name_col, ratio_col]].rename(columns={col_name_col: "Spalte", ratio_col: "Nullquote_%"})

        if isinstance(null_df, pd.DataFrame) and not null_df.empty:
            # Slider konfigurieren
            max_n = int(min(30, len(null_df))) if len(null_df) > 0 else 5
            default_n = int(min(10, len(null_df))) if len(null_df) > 0 else 5
            n = st.slider("Anzahl Spalten (Top N)", min_value=5, max_value=max(5, max_n), value=max(5, default_n), key="p1_topn")

            # Sortieren und Top N auswählen
            # Stelle sicher, dass die Quote numerisch ist
            null_df = null_df.copy()
            null_df["Nullquote_%"] = pd.to_numeric(null_df["Nullquote_%"], errors="coerce")
            null_df = null_df.dropna(subset=["Nullquote_%"]).sort_values("Nullquote_%", ascending=False).head(n)

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
        st.subheader("Null-Ratios nach Wochentag und Stunde")
        st.caption("Diese Heatmap visualisiert Konzentrationen der Null-Ratios im Zeitverlauf. Je intensiver der Rotton, desto höher war die prozentuale Fehlerquote am jeweiligen Wochentag zu der entsprechenden Uhrzeit.")
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
            st.caption("Hinweis: PLZ VN wird von OCR nicht gesetzt, daher extrem hohe Quoten an Wochenenden und nachts.")

        else:
            st.info("Keine Fehlerfrequenz-Daten verfügbar.")


    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)



# Chart 3: Avg. Positionen pro Auftrag über Monat (Trend)
    st.subheader("Positionen pro Auftrag über Zeit")

    if isinstance(pot_df, pd.DataFrame) and not pot_df.empty and {
        "Zeitperiode", "Avg_Positionen_pro_Auftrag", "Total_Positionen", "Anzahl_Auftraege"
    }.issubset(pot_df.columns):
        
        # 1. Daten vorbereiten (Datum konvertieren)
        work = pot_df.copy()
        try:
            work["Monat"] = pd.to_datetime(work["Zeitperiode"] + "-01", errors="coerce")
        except Exception:
            work["Monat"] = pd.to_datetime(work["Zeitperiode"], errors="coerce")
        
        work = work.dropna(subset=["Monat"]).sort_values("Monat").reset_index(drop=True)

        if not work.empty:
            min_date = work["Monat"].min().date()
            max_date = work["Monat"].max().date()

            # 2. Zeitraum-Slider einfügen
            # Wir nutzen st.slider mit value=(min, max) für einen Bereich
            col_filter, _ = st.columns([2, 1])
            with col_filter:
                selected_range = st.slider(
                    "Zeitraum eingrenzen:",
                    min_value=min_date,
                    max_value=max_date,
                    value=(min_date, max_date),
                    format="MMM YYYY"
                )

            # 3. Daten filtern
            mask = (work["Monat"].dt.date >= selected_range[0]) & (work["Monat"].dt.date <= selected_range[1])
            filtered_work = work.loc[mask].reset_index(drop=True)

            if not filtered_work.empty:
                # Ruhige Linie ohne Marker, dunkles Theme
                base = alt.Chart(filtered_work).encode(
                    x=alt.X("Monat:T", title="Monat")
                )

                # Y‑Achse dezent
                y_enc = alt.Y(
                    "Avg_Positionen_pro_Auftrag:Q",
                    title="Ø Positionen pro Auftrag",
                    scale=alt.Scale(zero=False, nice=True)
                )

                line = base.mark_line(color="#7c3aed", strokeWidth=2).encode(
                    y=y_enc,
                    tooltip=[
                        alt.Tooltip("yearmonth(Monat):T", title="Monat"),
                        alt.Tooltip("Avg_Positionen_pro_Auftrag:Q", title="Ø Pos./Auftrag", format=".2f"),
                        alt.Tooltip("Anzahl_Auftraege:Q", title="Anzahl Aufträge", format=","),
                        alt.Tooltip("Total_Positionen:Q", title="Summe Positionen", format=",")
                    ]
                )

                # Relevante Punkte: letztes, Maximum, Minimum innerhalb der Auswahl
                last_idx = len(filtered_work) - 1
                min_idx = int(filtered_work["Avg_Positionen_pro_Auftrag"].idxmin())
                max_idx = int(filtered_work["Avg_Positionen_pro_Auftrag"].idxmax())

                highlight_idx = sorted(set([i for i in [last_idx, min_idx, max_idx] if i is not None]))
                highlights = filtered_work.iloc[highlight_idx].copy()

                highlight_layer = (
                    alt.Chart(highlights)
                    .mark_point(filled=True, size=80, color="#e5e7eb", fill="#e5e7eb", opacity=0.9)
                    .encode(x="Monat:T", y=y_enc)
                )

                # Labels nur für Max/Min/Letzter
                if len(highlights) > 0:
                    highlights["Label"] = highlights.apply(
                        lambda r: "Max" if r.name == max_idx else ("Min" if r.name == min_idx else "Letzter Wert"), axis=1
                    )
                
                label_layer = (
                    alt.Chart(highlights)
                    .mark_text(dy=-10, color="#9ca3af", fontSize=11)
                    .encode(x="Monat:T", y=y_enc, text="Label:N")
                )

                chart = (line + highlight_layer + label_layer).properties(height=320, width="container")
                st.altair_chart(chart, width="stretch")

                # --- Insight-Text Logik (angepasst auf Auswahl) ---
                trend_text = ""
                trend_metric = None
                
                # Wir vergleichen Start der Auswahl vs. Ende der Auswahl
                if len(filtered_work) >= 2:
                    start_val = filtered_work.iloc[0]["Avg_Positionen_pro_Auftrag"]
                    last_val = filtered_work.iloc[-1]["Avg_Positionen_pro_Auftrag"]
                    
                    if pd.notna(start_val) and start_val != 0 and pd.notna(last_val):
                        delta_pct = (last_val - start_val) / start_val * 100
                        trend_metric = delta_pct
                        abs_delta = abs(delta_pct)

                        months_diff = (filtered_work.iloc[-1]["Monat"] - filtered_work.iloc[0]["Monat"]).days // 30
                        
                        zeitraum_str = f"im gewählten Zeitraum ({months_diff} Monate)"

                        if abs_delta < 2:
                            trend_text = f"Stabiler Verlauf {zeitraum_str}"
                        elif abs_delta < 8:
                            trend_text = "Leichter " + ("Anstieg" if delta_pct > 0 else "Rückgang") + f" {zeitraum_str}"
                        else:
                            trend_text = "Deutlicher " + ("Anstieg" if delta_pct > 0 else "Rückgang") + f" {zeitraum_str}"

                if trend_text == "":
                    trend_text = "Zeitraum zu kurz für Trendanalyse"

                # Ausgabe: Insight und Trendkennzahl
                st.caption(trend_text)
                if trend_metric is not None:
                    sign = "+" if trend_metric >= 0 else ""
                    # Farbe basierend auf Vorzeichen (optional)
                    color = "green" if trend_metric > 0 else "red" if trend_metric < 0 else "gray"
                    st.markdown(f"Veränderung Auswahl: :{color}[{sign}{trend_metric:.1f}%]")

            else:
                st.warning("Keine Daten im gewählten Zeitraum verfügbar.")
        else:
            st.info("Datensatz enthält keine gültigen Zeitangaben.")
    else:
        st.info("Keine Zeitreihendaten zu Positionen/Auftrag verfügbar.")