import streamlit as st
import metrics as mt


def show_page(df, df2, metrics_df1, metrics_df2, metrics_combined):
    
    
    plausi_diff_list_df1 = metrics_df1.get("plausi_forderung_einigung_list")
    plausi_count_df1 = metrics_df1.get("plausi_forderung_einigung_count")
    plausi_avg_df1 = metrics_df1.get("plausi_forderung_einigung_avg_diff")
    false_negative_df1 = metrics_df1.get("false_negatie", mt.false_negative_df(df))

    plausi_diff_list_df2 = metrics_df2.get("plausi_forderung_einigung_list")
    plausi_count_df2 = metrics_df2.get("plausi_forderung_einigung_count")
    plausi_avg_df2 = metrics_df2.get("plausi_forderung_einigung_avg_diff")
    discount_check = metrics_df2.get("discount_check_errors", mt.discount_check(df2))
    false_negative_df2 = metrics_df2.get("false_negatie", mt.false_negative_df2(df2))

    # --- KPIs ---
    plausi_cols = st.columns(4)
    with plausi_cols[0]: st.metric(label="Auftragsdaten: Einigung > Forderung", value=plausi_count_df1)
    with plausi_cols[1]: st.metric(label="Auftragsdaten: Durchschnittliche Abweichung", value=f"{plausi_avg_df1:.2f} €")
    with plausi_cols[2]: st.metric(label="Positionsdaten: Einigung > Forderung", value=plausi_count_df2)
    with plausi_cols[3]: st.metric(label="Auftragsdaten: Durchschnittliche Abweichung", value=f"{plausi_avg_df1:.2f} €")

    st.markdown("---")

    kpi_cols = st.columns(3)
    with kpi_cols[0]: st.metric(label="Positionsdaten: Potenziell fehlerhaftes Vorzeichen", value=discount_check) #braucht noch einen vernüftigen Namen
    with kpi_cols[1]: st.metric(label="Auftragsdaten: Inkorrekte Negative Beträge", value=false_negative_df1)
    with kpi_cols[2]: st.metric(label="Positionsdaten: Inkorrekte Negative Beträge", value=false_negative_df2)
    

    st.markdown("---")