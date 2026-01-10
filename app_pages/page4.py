import streamlit as st
import pandas as pd
import altair as alt
import metrics as mt


def show_page(df, df2, metrics_df1, metrics_df2, metrics_combined):
    discount_errors = metrics_df2.get("discount_check_errors", mt.discount_check(df2))
    proforma_df = metrics_df1.get("proforma_belege_df")
    proforma_count = metrics_df1.get("proforma_belege_count")
    fn_df1_count = metrics_df1.get("false_negative", mt.false_negative_df(df))
    fn_df2_count = metrics_df2.get("false_negative", mt.false_negative_df2(df2))

    total_df1 = len(df) if df is not None else 0
    total_df2 = len(df2) if df2 is not None else 0

    # Hilfsfunktionen (nur Frontend)
    def pct(n, total):
        if not total:
            return "0.00%"
        return f"{(n/total)*100:.2f}%"

    def euro(v):
        try:
            return f"{float(v):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return "–"

    def to_month(series, index=None):
        # robuste Monatsableitung (wie zuvor)
        if series is None:
            return pd.Series(pd.NaT, index=index) if index is not None else pd.Series(dtype="datetime64[ns]")
        if isinstance(series, (pd.Series, pd.Index)):
            dt = pd.to_datetime(series, errors="coerce")
            if isinstance(dt, pd.Index):
                dt = dt.to_series(index=index if index is not None else None)
        else:
            try:
                if index is not None and hasattr(index, "__len__") and len(index) > 1:
                    return pd.Series(pd.NaT, index=index)
                series = pd.Series(series)
            except Exception:
                return pd.Series(dtype="datetime64[ns]")
            dt = pd.to_datetime(series, errors="coerce")
        return dt.dt.to_period("M").dt.to_timestamp()

    def first_existing_column(df_local, candidates):
        return next((c for c in candidates if c in df_local.columns), None)

    # Layout: Fünf Tabs entsprechend 11–15
    tab11, tab12, tab13, tab14, tab15 = st.tabs([
        "11) Einigung > Forderung", "12) Rabatt/Vorzeichen", "13) Proforma-Belege", "14) Tripel-Vorzeichen (df1)", "15) Vorzeichen-Konsistenz (df2)"
    ])

    # 11) plausibilitaetscheck_forderung_einigung (df1/df2)
    with tab11:
        # Titel/Untertitel – reporting‑tauglich
        st.subheader("Plausibilitätscheck: Einigung > Forderung")
        st.caption("Fälle, in denen Einigung_Netto größer als Forderung_Netto ist")

        # Datensatz-Umschalter
        dataset = st.radio(
            "Datensatz",
            options=["Auftragsdaten (df1)", "Positionsdaten (df2)"],
            horizontal=True,
            index=0
        )

        if dataset.startswith("Auftragsdaten"):
            base_df = df if isinstance(df, pd.DataFrame) else pd.DataFrame()
            diffs_series = metrics_df1.get("plausi_forderung_einigung_list")
            diff_count = metrics_df1.get("plausi_forderung_einigung_count") or 0
            diff_avg = metrics_df1.get("plausi_forderung_einigung_avg_diff") or 0.0
            total_rows = len(base_df) if base_df is not None else 0
            id_col = "KvaRechnung_ID" if base_df is not None and "KvaRechnung_ID" in base_df.columns else None
        else:
            base_df = df2 if isinstance(df2, pd.DataFrame) else pd.DataFrame()
            diffs_series = metrics_df2.get("plausi_forderung_einigung_list")
            diff_count = metrics_df2.get("plausi_forderung_einigung_count") or 0
            diff_avg = metrics_df2.get("plausi_forderung_einigung_avg_diff") or 0.0
            total_rows = len(base_df) if base_df is not None else 0
            id_col = "Position_ID" if base_df is not None and "Position_ID" in base_df.columns else None

        # KPIs: Anzahl + Anteil, Gesamt, Median, P95 (Ø als Sekundärinfo)
        # Vorbereitung der Differenzen als DataFrame
        if isinstance(diffs_series, (pd.Series, list)):
            try:
                diffs_df = pd.DataFrame({"Diff": pd.to_numeric(pd.Series(diffs_series), errors="coerce")}).dropna()
            except Exception:
                diffs_df = pd.DataFrame(columns=["Diff"])  # leer
        else:
            diffs_df = pd.DataFrame(columns=["Diff"])  # leer

        med_val = float(diffs_df["Diff"].median()) if not diffs_df.empty else None
        p95_val = float(diffs_df["Diff"].quantile(0.95)) if not diffs_df.empty else None

        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.metric(
                label="Anzahl Fälle (Einigung > Forderung)",
                value=int(diff_count),
                delta=pct(int(diff_count), total_rows),
                delta_color="off",
            )
        with k2:
            st.metric(
                label="Gesamt Zeilen",
                value=total_rows,
            )
        with k3:
            st.metric(
                label="Median-Abweichung",
                value=(euro(med_val) if med_val is not None else "–"),
            )
        with k4:
            st.metric(
                label="P95-Abweichung",
                value=(euro(p95_val) if p95_val is not None else "–"),
            )
        with k5:
            st.metric(
                label="Ø-Abweichung (sekundär)",
                value=euro(diff_avg or 0),
            )

        # Kontext-Hinweis unter den KPIs
        if diffs_df.empty:
            st.info("Keine Abweichungen > 0 vorhanden oder Daten nicht verfügbar.")
        else:
            if p95_val is not None:
                st.caption(f"95 % der Fälle liegen unter {euro(p95_val)}; wenige Ausreißer treiben den Durchschnitt nach oben.")
            else:
                st.caption("Keine aussagekräftigen Perzentile berechenbar.")

        # Histogramme entkoppelt von Ausreißern: Option A (zwei Histogramme)
        if not diffs_df.empty:
            # Bestimme P95-Grenze
            p95_val = float(diffs_df["Diff"].quantile(0.95))
            main_df = diffs_df[diffs_df["Diff"] <= p95_val]
            out_df = diffs_df[diffs_df["Diff"] > p95_val]
            main_count = len(main_df)
            out_count = len(out_df)

            # Optional: Impact-KPI für Ausreißer – nur auf Wunsch
            with st.expander("Optionale Impact-KPI (nur Ausreißer)", expanded=False):
                if out_count > 0:
                    out_sum = float(out_df["Diff"].sum())
                    st.metric(
                        label="Summe der Abweichungen (nur Ausreißer)",
                        value=euro(out_sum)
                    )
                else:
                    st.info("Keine Ausreißer oberhalb P95 vorhanden – keine Impact-KPI.")

            c1, c2 = st.columns(2)
            with c1:
                title = f"Hauptverteilung (P0–P95, n={main_count})"
                hist_main = alt.Chart(main_df).mark_bar(color="#1F77B4").encode(
                    x=alt.X("Diff:Q", bin=alt.Bin(maxbins=35), title="Abweichung (Einigung − Forderung) in €"),
                    y=alt.Y("count():Q", title="Anzahl"),
                    tooltip=[alt.Tooltip("count():Q", title="Anzahl"), alt.Tooltip("Diff:Q", title="Abweichung", format=",")],
                ).properties(height=320, title=title)
                st.altair_chart(hist_main, use_container_width=True)
                st.caption(f"Abdeckung: ca. 95 % der Fälle ≤ {euro(p95_val)}")
            with c2:
                # NEU: Top-10 Outlier Bar (anstelle des Ausreißer-Histogramms)
                if out_count == 0:
                    st.info("Keine Ausreißer oberhalb der P95-Schwelle")
                else:
                    # Kontextinformationen
                    st.caption(f"P95-Schwelle: {euro(p95_val)}  •  Ausreißer-Anteil: {out_count} von {total_rows} Fällen ({pct(out_count, total_rows)})")

                    # Benötigte Spalten prüfen
                    needed_cols_ids = [c for c in ["KvaRechnung_ID", "Position_ID"] if isinstance(base_df, pd.DataFrame) and c in base_df.columns]
                    needed_cols_vals = [c for c in ["Forderung_Netto", "Einigung_Netto"] if isinstance(base_df, pd.DataFrame) and c in base_df.columns]

                    if not isinstance(base_df, pd.DataFrame) or base_df.empty or len(needed_cols_vals) < 2:
                        st.warning("Erforderliche Spalten fehlen oder keine Daten verfügbar für die Ausreißer‑Aufbereitung.")
                    else:
                        work = base_df[[*(needed_cols_ids or []), *needed_cols_vals]].copy()
                        # Differenz berechnen wie in der Metrik definiert
                        work["Diff"] = (work["Einigung_Netto"] - work["Forderung_Netto"]).round(2)
                        # Nur positive Abweichungen betrachten und oberhalb P95 filtern
                        work = work[work["Diff"] > p95_val].copy()

                        # ID-Spalte bestimmen
                        id_field = None
                        if dataset.startswith("Auftragsdaten"):
                            id_field = "KvaRechnung_ID" if "KvaRechnung_ID" in work.columns else None
                        else:
                            # Positionsdaten: bevorzugt Position_ID, optional kombinierte ID
                            if "Position_ID" in work.columns and "KvaRechnung_ID" in work.columns:
                                work["ID"] = work["KvaRechnung_ID"].astype(str) + " – " + work["Position_ID"].astype(str)
                                id_field = "ID"
                            elif "Position_ID" in work.columns:
                                id_field = "Position_ID"
                            elif "KvaRechnung_ID" in work.columns:
                                id_field = "KvaRechnung_ID"

                        if id_field is None:
                            # Fallback: künstliche ID aus Index
                            work = work.reset_index().rename(columns={"index": "ID"})
                            id_field = "ID"

                        # Sortieren und Top 10 wählen
                        work = work.sort_values("Diff", ascending=False)
                        top_n = min(10, len(work))
                        work_top = work.head(top_n).copy()
                        if top_n == 0:
                            st.info("Keine Ausreißer oberhalb der P95-Schwelle")
                        else:
                            # Tooltip-Felder (optional vorhandene Zusatzinfos)
                            optional_cols = [c for c in ["CRMEingangszeit", "Kundengruppe", "Gewerk_Name", "Gewerk"] if c in base_df.columns]
                            tooltip_fields = [
                                alt.Tooltip(f"{id_field}:N", title="ID"),
                                alt.Tooltip("Forderung_Netto:Q", title="Forderung_Netto", format=",.2f"),
                                alt.Tooltip("Einigung_Netto:Q", title="Einigung_Netto", format=",.2f"),
                                alt.Tooltip("Diff:Q", title="Abweichung", format=",.2f"),
                            ] + [alt.Tooltip(f"{c}:N", title=c) for c in optional_cols]

                            title = f"Top {top_n} Ausreißer (Diff > P95)"
                            bars = alt.Chart(work_top).mark_bar(color="#E4572E").encode(
                                x=alt.X("Diff:Q", title="Abweichung (Einigung − Forderung) in €", axis=alt.Axis(format=",.2f")),
                                y=alt.Y(f"{id_field}:N", sort='-x', title=("KvaRechnung_ID" if dataset.startswith("Auftragsdaten") else "ID")),
                                tooltip=tooltip_fields,
                            ).properties(height=max(200, 30 * top_n), title=title)

                            # Wertlabel am Balkenende
                            labels = bars.mark_text(align='left', baseline='middle', dx=3, color="#333").encode(
                                text=alt.Text("Diff:Q", format=",.2f")
                            )

                            st.altair_chart(bars + labels, use_container_width=True)
                            st.caption("Größte Abweichungen sortiert nach Höhe (Einigung − Forderung)")

            # Einheitliche Farblogik transparent machen
            st.caption("Farblogik: Blau = Hauptverteilung, Orange = Ausreißer")

        # Top‑Tabelle: Top 50 Abweichungen
        needed_cols = ["Forderung_Netto", "Einigung_Netto"]
        if base_df is None or base_df.empty or not all(c in base_df.columns for c in needed_cols):
            st.warning("Erforderliche Spalten fehlen oder keine Daten vorhanden für die Top‑Tabelle.")
        else:
            tmp = base_df[[c for c in needed_cols + ([id_col] if id_col else [])]].copy()
            tmp["Diff"] = (tmp["Einigung_Netto"] - tmp["Forderung_Netto"]).round(2)
            tmp = tmp[tmp["Diff"] > 0]
            tmp = tmp.sort_values("Diff", ascending=False)
            # Spaltenreihenfolge
            cols = ([id_col] if id_col else []) + ["Forderung_Netto", "Einigung_Netto", "Diff"]
            top_table = tmp[cols].head(520)
            with st.expander("Top 50 Abweichungen (Tabelle)", expanded=True):
                st.dataframe(top_table, use_container_width=True)
                st.download_button(
                    "CSV herunterladen",
                    data=top_table.to_csv(index=False).encode("utf-8"),
                    file_name=("plausi_einigung_gt_forderung_top50_df1.csv" if dataset.startswith("Auftragsdaten") else "plausi_einigung_gt_forderung_top50_df2.csv"),
                    mime="text/csv",
                )

    # 12) discount_check (df2)
    with tab12:
        st.subheader("12) Rabatt erkannt – Werte sign-konsistent?")
        k1, k2 = st.columns(2)
        with k1:
            st.metric(
                label="Auffällige Positionen (Regelverletzung)",
                value=int(discount_errors or 0),
                delta=pct(int(discount_errors or 0), total_df2),
                delta_color="off"
            )
        with k2:
            st.metric(
                label="Gesamt Positionen",
                value=total_df2,
            )

        # Kontexttext direkt unter den KPIs
        st.caption("Eine Auffälligkeit bedeutet eine Verletzung der Vorzeichenregel bei erkannten Rabattpositionen und ist kein bestätigter Fehler.")

        # Breakdown Bar: Fehler nach Positionstyp/Bezeichnung
        if "Plausibel" in df2.columns:
            df_err = df2[df2["Plausibel"] == False].copy()
            # Label-Spalte aus dem Gesamtdatenbestand bestimmen (nicht nur den Fehlern)
            label_col = first_existing_column(df2, ["Positionstyp", "Bezeichnung", "Text", "Kurztext"]) or "Bezeichnung"
            if df_err.empty:
                st.info("Keine unplausiblen Positionen vorhanden.")
            else:
                # Fehler je Bezeichnung
                breakdown_err = (
                    df_err.groupby(label_col, observed=True)
                    .size()
                    .reset_index(name="Fehler")
                )
                # Gesamt je Bezeichnung (Basis für Quote)
                breakdown_total = (
                    df2.groupby(label_col, observed=True)
                    .size()
                    .reset_index(name="Total")
                )
                breakdown = breakdown_total.merge(breakdown_err, on=label_col, how="left")
                breakdown["Fehler"] = breakdown["Fehler"].fillna(0).astype(int)
                breakdown["Total"] = breakdown["Total"].fillna(0).astype(int)
                # Ohne Baseline (Total==0) keine Balken anzeigen
                breakdown = breakdown[breakdown["Total"] > 0]
                # Fehlerquote als Anteil
                breakdown["Fehlerquote"] = breakdown.apply(lambda r: (r["Fehler"] / r["Total"]) if r["Total"] else 0.0, axis=1)

                # Sortier-Toggle
                sort_choice = st.radio(
                    "Sortieren nach",
                    options=["Anzahl", "Fehlerquote (%)"],
                    horizontal=True,
                    index=0,
                    help="Default: Anzahl (operativ priorisieren). Optional: Fehlerquote (%) für analytische Sicht."
                )

                if sort_choice == "Fehlerquote (%)":
                    breakdown = breakdown.sort_values(["Fehlerquote", "Fehler"], ascending=[False, False])
                    st.caption("Analysemodus: Sortiert nach Fehlerquote (%) – berücksichtigt die jeweilige Basis (Gesamt je Bezeichnung).")
                else:
                    breakdown = breakdown.sort_values(["Fehler", "Fehlerquote"], ascending=[False, False])

                # Top-N (15) auswählen
                breakdown_top = breakdown.head(15).copy()

                if breakdown_top.empty:
                    st.info("Keine anzeigbaren Bezeichnungen (fehlende Basis oder keine Auffälligkeiten).")
                    st.stop()

                # Reihenfolge für Achsensort explizit festlegen
                order_labels = breakdown_top[label_col].tolist()

                # Chart: Count als Balken, Quote als Label/Tooltip
                # Kombiniertes Label: absolute Anzahl + Quote
                breakdown_top["LabelText"] = breakdown_top.apply(lambda r: f"{r['Fehler']} | {r['Fehlerquote']:.1%}", axis=1)

                bar = alt.Chart(breakdown_top).mark_bar(color="#E4572E").encode(
                    x=alt.X("Fehler:Q", title="Anzahl Auffälligkeiten"),
                    y=alt.Y(f"{label_col}:N", sort=order_labels, title=label_col),
                    tooltip=[
                        alt.Tooltip(f"{label_col}:N", title=label_col),
                        alt.Tooltip("Fehler:Q", title="Auffälligkeiten"),
                        alt.Tooltip("Total:Q", title="Gesamt Positionen"),
                        alt.Tooltip("Fehlerquote:Q", title="Fehlerquote", format=".1%"),
                    ],
                ).properties(height=max(320, 18 * len(order_labels)))

                # Labels am Balkenende: absolute Anzahl | Quote
                labels = bar.mark_text(align="left", baseline="middle", dx=3, color="#333").encode(
                    text=alt.Text("LabelText:N")
                )

                st.altair_chart(bar + labels, use_container_width=True)

                with st.expander("Beispiele (Tabelle)"):
                    cols = [c for c in ["Position_ID", label_col, "Forderung_Netto", "Einigung_Netto", "Plausibel"] if c in df_err.columns]
                    st.dataframe(df_err[cols] if cols else df_err, use_container_width=True)
                    st.download_button(
                        "CSV herunterladen",
                        data=(df_err[cols] if cols else df_err).to_csv(index=False).encode("utf-8"),
                        file_name="discount_check_unplausibel.csv",
                        mime="text/csv",
                    )
        else:
            st.warning("Spalte 'Plausibel' fehlt in df2 – keine Aufschlüsselung möglich.")

    # 13) proformabelege (df1)
    with tab13:
        st.subheader("13) Proforma-Belege finden")
        proforma = proforma_df if isinstance(proforma_df, pd.DataFrame) else pd.DataFrame(columns=df.columns)
        k1, k2 = st.columns(2)
        with k1:
            st.metric(
                label="Erkannte Proforma-Belege",
                value=int(proforma_count or 0),
                delta=pct(int(proforma_count or 0), total_df1),
                delta_color="off"
            )
        with k2:
            st.metric(label="Gesamt Aufträge", value=total_df1)

        # Kontext: Es geht um Erkennung, nicht um Volumen
        st.caption("Hinweis: Es handelt sich um erkannte Proforma-Belege (Erkennung), nicht um Rechnungsvolumen.")

        if proforma.empty:
            st.info("Keine Proforma-Belege gefunden.")
        else:
            with st.expander("Proforma-Fälle (Tabelle)", expanded=True):
                cols = [c for c in ["KvaRechnung_ID", "Einigung_Netto", "CRMEingangszeit"] if c in proforma.columns]
                table = proforma[cols] if cols else proforma
                st.dataframe(table, use_container_width=True)
                st.download_button(
                    "CSV herunterladen",
                    data=table.to_csv(index=False).encode("utf-8"),
                    file_name="proforma_belege.csv",
                    mime="text/csv",
                )

            # Optional: Trend pro Monat
            if "CRMEingangszeit" in proforma.columns:
                pf = proforma.copy()
                pf["Monat"] = to_month(pf["CRMEingangszeit"], index=pf.index)
                monthly = pf.dropna(subset=["Monat"]).groupby("Monat", observed=True).size().reset_index(name="Count")
                if not monthly.empty:
                    line = alt.Chart(monthly).mark_line(point=True).encode(
                        x=alt.X("Monat:T", title="Monat"),
                        y=alt.Y("Count:Q", title="Proforma je Monat"),
                        tooltip=["Monat:T", "Count:Q"],
                    ).properties(height=320, title="Proforma-Belege pro Monat")
                    st.altair_chart(line, use_container_width=True)
                    st.caption("Zeitlicher Verlauf erkannter Proforma-Belege")

    # 14) false_negative_df (df1)
    with tab14:
        st.subheader("14) Wenn 2 von 3 negativ sind, muss das dritte auch negativ sein (df1)")
        k1, k2 = st.columns(2)
        with k1:
            st.metric(
                label="Fehleranzahl",
                value=int(fn_df1_count or 0),
                delta=pct(int(fn_df1_count or 0), total_df1),
                delta_color="off",
            )
        with k2:
            st.metric(label="Gesamt Aufträge", value=total_df1)

        # Breakdown nach betroffener Spalte
        if all(col in df.columns for col in ["Forderung_Netto", "Empfehlung_Netto", "Einigung_Netto"]):
            masks = {
                "Einigung_Netto": (df["Einigung_Netto"] < 0) & ~((df["Forderung_Netto"] < 0) & (df["Empfehlung_Netto"] < 0)),
                "Empfehlung_Netto": (df["Empfehlung_Netto"] < 0) & ~((df["Forderung_Netto"] < 0) & (df["Einigung_Netto"] < 0)),
                "Forderung_Netto": (df["Forderung_Netto"] < 0) & ~((df["Einigung_Netto"] < 0) & (df["Empfehlung_Netto"] < 0)),
            }
            rows = []
            for col, m in masks.items():
                rows.append({"Spalte": col, "Fehler": int(m.sum())})
            breakdown = pd.DataFrame(rows)
            bar = alt.Chart(breakdown).mark_bar().encode(
                x=alt.X("Fehler:Q", title="Anzahl Fehler"),
                y=alt.Y("Spalte:N", sort='-x', title="Betroffene Spalte"),
                tooltip=["Spalte:N", "Fehler:Q"],
            ).properties(height=300)
            st.altair_chart(bar, use_container_width=True)

            # Beispielzeilen nach "Schwere" sortiert (größter Betrag)
            sample_mask = masks["Einigung_Netto"] | masks["Empfehlung_Netto"] | masks["Forderung_Netto"]
            examples = df.loc[sample_mask, ["KvaRechnung_ID", "Forderung_Netto", "Empfehlung_Netto", "Einigung_Netto"]].copy()
            if not examples.empty:
                examples["Schwere"] = examples[["Forderung_Netto", "Empfehlung_Netto", "Einigung_Netto"]].abs().max(axis=1)
                examples = examples.sort_values("Schwere", ascending=False)
                with st.expander("Beispiele (nach Schwere sortiert)"):
                    st.dataframe(examples, use_container_width=True)
                    st.download_button(
                        "CSV herunterladen",
                        data=examples.to_csv(index=False).encode("utf-8"),
                        file_name="false_negative_df1_beispiele.csv",
                        mime="text/csv",
                    )
            else:
                st.info("Keine Beispielzeilen vorhanden.")
        else:
            st.warning("Erforderliche Spalten fehlen in df1.")

    # 15) false_negative_df2 (df2)
    with tab15:
        st.subheader("15) Negative Werte in Menge/EP/Beträgen konsistent? (df2)")
        k1, k2 = st.columns(2)
        with k1:
            st.metric(
                label="Total Errors",
                value=int(fn_df2_count or 0),
                delta=pct(int(fn_df2_count or 0), total_df2),
                delta_color="off",
            )
        with k2:
            st.metric(label="Gesamt Positionen", value=total_df2)

        # Kategorien bestimmen: Menge, Menge_Einigung, EP vs EP_Einigung, Forderung vs Einigung
        categories = []
        if "Menge" in df2.columns:
            categories.append(("Menge", df2["Menge"] < 0))
        if "Menge_Einigung" in df2.columns:
            categories.append(("Menge_Einigung", df2["Menge_Einigung"] < 0))
        if all(c in df2.columns for c in ["EP", "EP_Einigung"]):
            categories.append(("EP vs EP_Einigung", (df2["EP"] < 0) ^ (df2["EP_Einigung"] < 0)))
        if all(c in df2.columns for c in ["Forderung_Netto", "Einigung_Netto"]):
            categories.append(("Forderung vs Einigung", (df2["Forderung_Netto"] < 0) ^ (df2["Einigung_Netto"] < 0)))

        if categories:
            breakdown_rows = [{"Kategorie": name, "Fehler": int(mask.fillna(False).sum())} for name, mask in categories]
            breakdown2 = pd.DataFrame(breakdown_rows).sort_values("Fehler", ascending=False)
            bar2 = alt.Chart(breakdown2).mark_bar().encode(
                x=alt.X("Fehler:Q", title="Anzahl Fehler"),
                y=alt.Y("Kategorie:N", sort='-x'),
                tooltip=["Kategorie:N", "Fehler:Q"],
            ).properties(height=320)
            st.altair_chart(bar2, use_container_width=True)

            # Tabelle: Beispielzeilen mit markierten Regeln
            rules = []
            for name, mask in categories:
                rules.append(pd.Series(mask.fillna(False), name=name))
            rules_df = pd.concat(rules, axis=1)
            violated = rules_df.any(axis=1)
            if violated.any():
                examples2 = df2.loc[violated, [c for c in [
                    "Position_ID", "Menge", "Menge_Einigung", "EP", "EP_Einigung", "Forderung_Netto", "Einigung_Netto"
                ] if c in df2.columns]].copy()
                examples2["Regel"] = rules_df.loc[violated].apply(lambda r: ", ".join([col for col, v in r.items() if v]), axis=1)
                # Begrenzen für Anzeige
                examples2 = examples2.head(1000)
                with st.expander("Beispiele (verletzte Regeln)", expanded=False):
                    st.dataframe(examples2, use_container_width=True)
                    st.download_button(
                        "CSV herunterladen",
                        data=examples2.to_csv(index=False).encode("utf-8"),
                        file_name="false_negative_df2_beispiele.csv",
                        mime="text/csv",
                    )
            else:
                st.info("Keine verletzten Regeln gefunden.")
        else:
            st.warning("Keine geeigneten Spalten für die Kategorien gefunden.")

    st.markdown("---")