import pandas as pd
import numpy as np
import duckdb
import time
import metrics as mt

DB_PATH = "resources/dashboard_data.duckdb"
start_time = time.time()

print("--- Step 1: Loading Data ---")
df = pd.read_parquet("resources/Auftragsdaten")
df2 = pd.read_parquet("resources/Positionsdaten")
df3 = pd.read_parquet("resources/Auftragsdaten_Zeit")

print("--- Step 2: Merging & Cleaning ---")
df = pd.merge(df, df3, on='KvaRechnung_ID', how='left')
df = df.drop(["Auftrag_ID_y", "Schadensnummer_y"], axis=1)
df = df.rename(columns={'Auftrag_ID_x': 'AuftragID', 'Schadensnummer_x': 'Schadensnummer'})

df = pd.merge(df, mt.position_count(df2), on='KvaRechnung_ID', how='left')

# Pre-cleaning memory check
print(f"Memory usage before converting:")
df.info(memory_usage='deep')

None_placeholder = ["-", "(leer)", "(null)", "wird vergeben", "unbekannter HW", "#unbekannter hw", "Allgemeine Standardbeschreibungen"]
for placeholder in None_placeholder:
    df = df.replace(placeholder, pd.NA)
    df2 = df2.replace(placeholder, pd.NA)

# Replace Typing Errors
df = df.replace("Betriebsunterbrechnung", "Betriebsunterbrechung")
df = df.replace("Überpannung Heizung", "Überspannung Heizung")
df = df.replace("Kfz", "KFZ")
df = df.replace("Schliessanlagen", "Schließanlagen")

# --- Optimizing Types for DF (Auftragsdaten) ---
columns_to_convert = ['Land', 'PLZ_SO', 'PLZ_HW', 'PLZ_VN', 'address1_postalcode',
                       'Schadenart_Name', 'Falltyp_Name', 'Gewerk_Name', 'Kundengruppe',
                       'Handwerker_Name']

# Convert Object to Category
df[columns_to_convert] = df[columns_to_convert].astype('category')

# Convert objects to String
object_columns = df.select_dtypes('object').columns
df[object_columns] = df[object_columns].astype('string')

# Downcast integers
int_cols = df.select_dtypes(include=['int64']).columns
for col in int_cols:
    df[col] = pd.to_numeric(df[col], downcast='integer')

# Downcast floats
df_below_four_decimals = df.select_dtypes(include='float') \
                                    .apply(lambda col: np.isclose(col, col.round(4))) \
                                    .any() \
                                    .loc[lambda s: s] \
                                    .index.tolist()
df[df_below_four_decimals] = df[df_below_four_decimals].astype('float32')

# --- Optimizing Types for DF2 (Positionsdaten) ---
df2_columns_to_convert = ['KvaRechnung_ID', 'KvaRechnung_Nummer', 'Mengeneinheit', 'Bemerkung']
df2[df2_columns_to_convert] = df2[df2_columns_to_convert].astype('category')

object_columns_df2 = df2.select_dtypes('object').columns
df2[object_columns_df2] = df2[object_columns_df2].astype('string')

df2_below_four_decimals = df2.select_dtypes(include='float') \
                                    .apply(lambda col: np.isclose(col, col.round(4))) \
                                    .any() \
                                    .loc[lambda s: s] \
                                    .index.tolist()
df2[df2_below_four_decimals] = df2[df2_below_four_decimals].astype('float32')

# Post-cleaning memory check
print(f"Memory usage after converting (Ready for DB):")
df.info(memory_usage='deep')

# Logic for Discounts/Plausibility
keywords = ["Rabatt", "Skonto", "Nachlass", "Gutschrift", "Bonus", "Abzug", "Minderung", "Gutschein", "Erlass", "Storno", "Kulanz"]
pattern = '|'.join(keywords)
df2['ist_Abzug'] = df2['Bezeichnung'].str.contains(pattern, case=False, regex=True, na=False)

normal_position = (df2['Einigung_Netto'] > 0) & (df2['ist_Abzug'] == False)
discount_position = (df2['Einigung_Netto'] < 0) & (df2['ist_Abzug'] == True)
df2['Plausibel'] = normal_position | discount_position


print("--- Step 3: Building DuckDB Database ---")
con = duckdb.connect(DB_PATH)

# Store the "Original" Cleaned Data
print("Saving (Auftragsdaten)...")
con.execute("CREATE OR REPLACE TABLE auftragsdaten AS SELECT * FROM df")

print("Saving (Positionsdaten)...")
con.execute("CREATE OR REPLACE TABLE positionsdaten AS SELECT * FROM df2")



print("--- Step 4: Calculating Scalar Metrics ---")

# --- 1. General Counts ---
total_orders = mt.count_rows(df)
total_positions = mt.count_rows(df2)

# --- 2. Data Quality (Nulls & Uniqueness) ---
null_ratio_orders = mt.ratio_null_values_rows(df)
null_ratio_positions = mt.ratio_null_values_rows(df2)
unique_kva, unique_pos = mt.uniqueness_check(df, df2)

# --- 3. Business Logic / Test Data ---
test_data_count = mt.Kundengruppe_containing_test(df, return_frame=False)

# --- 4. Plausibility Checks (Tuples extraction) ---
# returns: (Series, count, avg) -> ignore the Series (_)
_, plausibility_error_count, plausibility_avg_diff = mt.plausibilitaetscheck_forderung_einigung(df)

# returns: (DataFrame, count) -> ignore the DataFrame (_)
_, proforma_count = mt.proformabelege(df)

# --- 5. Logic Errors ---
discount_logic_errors = mt.discount_check(df2)
false_negative_df = mt.false_negative_df(df)
false_negative_df2 = mt.false_negative_df2(df2)


print("--- Step 5: Constructing Scalar Metrics Table ---")

kpi_data = {
    # General
    'count_total_orders': [total_orders],
    'count_total_positions': [total_positions],

    # Quality
    'null_row_ratio_orders': [null_ratio_orders],
    'null_row_ratio_positions': [null_ratio_positions],
    'is_unique_kva_id': [unique_kva],
    'is_unique_position_id': [unique_pos],

    # Test Data
    'count_test_data_rows': [test_data_count],

    # Logic Errors
    'count_plausibility_errors': [plausibility_error_count],
    'avg_plausibility_diff': [plausibility_avg_diff],
    'count_proforma_receipts': [proforma_count],
    'count_discount_logic_errors': [discount_logic_errors],
    'count_false_negative_df': [false_negative_df],
    'count_false_negative_df2': [false_negative_df2]
}

df_scalars = pd.DataFrame(kpi_data)

print("--- Step 6: Saving to DuckDB ---")
con.execute("CREATE OR REPLACE TABLE scalar_metrics AS SELECT * FROM df_scalars")



print("--- Step 7: Computing Complex Metrics and Creating Tables ---")

# 1. Null Ratios per Column (Returns DataFrame)
print("1. Null Ratios")
df_null_ratios = mt.ratio_null_values_column(df)
con.execute("CREATE OR REPLACE TABLE metric_null_ratios_per_column AS SELECT * FROM df_null_ratios")

# 2. Test Data Entries (Returns (int, DataFrame) -> we want the DF)
print("2. Test Data Check")
_, df_test_rows = mt.Kundengruppe_containing_test(df, return_frame=True)
if not df_test_rows.empty:
    con.execute("CREATE OR REPLACE TABLE metric_test_data_entries AS SELECT * FROM df_test_rows")
else:
    # Create empty table with schema if no data found
    con.execute("CREATE OR REPLACE TABLE metric_test_data_entries AS SELECT * FROM df WHERE 1=0")

# 3. Numeric Statistics (Returns Dict -> Convert to DF)
print("3. Numeric Stats")
stats_dict_df = mt.allgemeine_statistiken_num(df)
# Transpose so columns are 'mean', 'std', etc., and index is the column name
df_stats_df = pd.DataFrame(stats_dict_df).T.reset_index().rename(columns={'index': 'column_name'})
con.execute("CREATE OR REPLACE TABLE metric_numeric_stats_auftragsdaten AS SELECT * FROM df_stats_df")

stats_dict_df2 = mt.allgemeine_statistiken_num(df2)
# Transpose so columns are 'mean', 'std', etc., and index is the column name
df_stats_df2 = pd.DataFrame(stats_dict_df2).T.reset_index().rename(columns={'index': 'column_name'})
con.execute("CREATE OR REPLACE TABLE metric_numeric_stats_positionsdaten AS SELECT * FROM df_stats_df2")

# 4. Plausibility Check (Returns (Series, int, avg) -> only extract the Series)
print("4. Plausibility Differences")
series_diffs_df, _, _ = mt.plausibilitaetscheck_forderung_einigung(df)
df_plausi_df = series_diffs_df.to_frame(name='differenz_eur').reset_index().rename(columns={'index': 'original_row_index'})
con.execute("CREATE OR REPLACE TABLE metric_plausibility_diffs_auftragsdaten AS SELECT * FROM df_plausi_df")

series_diffs_df2, _, _ = mt.plausibilitaetscheck_forderung_einigung(df2)
df_plausi_df2 = series_diffs_df2.to_frame(name='differenz_eur').reset_index().rename(columns={'index': 'original_row_index'})
con.execute("CREATE OR REPLACE TABLE metric_plausibility_diffs_positionsdaten AS SELECT * FROM df_plausi_df2")

# 5. Data Cleanliness Grouped (Returns (Series, DataFrame))
print("5. Data Cleanliness Grouped")
series_row_ratios_grouped_df, df_col_ratios_grouped_df = mt.data_cleanliness(df, group_by_col="Kundengruppe")

# Reset index to make 'Kundengruppe' a real column
# df_clean_cols_df = df_col_ratios_grouped_df.reset_index()
con.execute("CREATE OR REPLACE TABLE metric_cleanliness_cols_grouped_auftragsdaten AS SELECT * FROM df_col_ratios_grouped_df")

# Handle the Series part (Rows)
df_clean_rows_df = series_row_ratios_grouped_df.to_frame(name='row_null_ratio').reset_index()
con.execute("CREATE OR REPLACE TABLE metric_cleanliness_rows_grouped_auftragsdaten AS SELECT * FROM df_clean_rows_df")


print("6. Data Cleanliness Ungrouped")
_, df_col_ratios_ungrouped_df = mt.data_cleanliness(df, group_by_col=None)
df_col_ratios_ungrouped_df = df_col_ratios_ungrouped_df.rename(columns={'index': 'column_name'})
con.execute("CREATE OR REPLACE TABLE metric_cleanliness_cols_ungrouped_auftragsdaten AS SELECT * FROM df_col_ratios_ungrouped_df")

_, df_col_ratios_ungrouped_df2 = mt.data_cleanliness(df2, group_by_col=None)
df_col_ratios_ungrouped_df2 = df_col_ratios_ungrouped_df2.rename(columns={'index': 'column_name'})
con.execute("CREATE OR REPLACE TABLE metric_cleanliness_cols_ungrouped_positionsdaten AS SELECT * FROM df_col_ratios_ungrouped_df2")


# 7. Proforma Receipts Returns (DataFrame, int)
print("7. Proforma Receipts")
df_proforma, _ = mt.proformabelege(df)
con.execute("CREATE OR REPLACE TABLE metric_proforma AS SELECT * FROM df_proforma")

# 8. High Value > 50k (Returns DataFrame)
print("8. Suspiciously high Value")
df_above_50k = mt.above_50k(df)
con.execute("CREATE OR REPLACE TABLE metric_above_50k AS SELECT * FROM df_above_50k")

# 9. Zeitwert Errors (Returns Series -> Convert to DF)
print("9. Zeitwert Errors")
zeitwert = mt.check_zeitwert(df)
#df_zeitwert = zeitwert.to_frame(name='zeitwert_diff')
con.execute("CREATE OR REPLACE TABLE metric_zeitwert_errors AS SELECT * FROM zeitwert")

# 10. Positions over Time (Returns DataFrame)
print("10. Positions Over Time")
df_pos_time = mt.positions_per_order_over_time(df, df2, time_col="CRMEingangszeit")
con.execute("CREATE OR REPLACE TABLE metric_positions_over_time AS SELECT * FROM df_pos_time")

# 11. Error Frequency Heatmap (Returns DataFrame)
print("11. Error Frequency Heatmap")
df_heatmap = mt.error_frequency_by_weekday_hour(df, time_col="CRMEingangszeit")
con.execute("CREATE OR REPLACE TABLE metric_error_heatmap AS SELECT * FROM df_heatmap")

# 12. Order vs Position Financial Mismatch (Returns DataFrame)
print("12. Order/Position Mismatch")
df_mismatch = mt.abgleich_auftraege(df, df2)
con.execute("CREATE OR REPLACE TABLE metric_order_pos_mismatch AS SELECT * FROM df_mismatch")

# 13. Handwerker Outliers
print("13. Handwerker Outliers")
df_outlier = mt.handwerker_gewerke_outlier(df)
df_outliers_true = df_outlier[df_outlier['is_outlier'] == True].copy()
df_outliers_true['Check_Result'] = mt.check_keywords_vectorized(df_outliers_true)
con.execute("CREATE OR REPLACE TABLE metric_handwerker_outliers AS SELECT * FROM df_outliers_true")

print("14. Semantic Handwerker Mismatches")
#df_semantic = mt.get_mismatched_entries(df)
#con.execute("CREATE OR REPLACE TABLE metric_semantic_mismatches AS SELECT * FROM df_semantic")
df_semantic = []
# Optional: Leere Tabelle in DB anlegen, falls das Dashboard danach sucht
con.execute("CREATE OR REPLACE TABLE metric_semantic_mismatches AS SELECT 'dummy' as col1 WHERE 1=0")

print("Calculating Extended Chart Data...")
# page4 Tab 1
plausi_outliers = mt.get_plausi_outliers(df)
con.execute("CREATE OR REPLACE TABLE metric_plausi_outliers_df1 AS SELECT * FROM plausi_outliers")
plausi_outliers2 = mt.get_plausi_outliers_df2(df2)
con.execute("CREATE OR REPLACE TABLE metric_plausi_outliers_df2 AS SELECT * FROM plausi_outliers2")

# page4 Tab 2
disc_stats, disc_details = mt.get_discount_details(df2)
con.execute("CREATE OR REPLACE TABLE metric_discount_stats AS SELECT * FROM disc_stats")
con.execute("CREATE OR REPLACE TABLE metric_discount_details AS SELECT * FROM disc_details")

# page4 Tab 4
fn_stats1, fn_details1 = mt.get_fn_df1_details(df)
con.execute("CREATE OR REPLACE TABLE metric_fn_stats_df1 AS SELECT * FROM fn_stats1")
con.execute("CREATE OR REPLACE TABLE metric_fn_details_df1 AS SELECT * FROM fn_details1")

# page4 Tab 5
fn_stats2, fn_details2 = mt.get_fn_df2_details(df2)
con.execute("CREATE OR REPLACE TABLE metric_fn_stats_df2 AS SELECT * FROM fn_stats2")
con.execute("CREATE OR REPLACE TABLE metric_fn_details_df2 AS SELECT * FROM fn_details2")

print("--- Step 8: Calculating overall Issue Metric ---")
numeric_issues = len(zeitwert) + len(df_above_50k) + len(df_mismatch)
text_issues = test_data_count + len(df_outliers_true) + len(df_semantic)
plausi_issues = plausibility_error_count + discount_logic_errors + proforma_count + false_negative_df + false_negative_df2
overall_issues = numeric_issues + text_issues + plausi_issues

issues = {
    'numeric_issues': [numeric_issues],
    'text_issues': [text_issues],
    'plausi_issues': [plausi_issues],
    'overall_issues': [overall_issues]
}

df_issues = pd.DataFrame(issues)
print(df_issues)
con.execute("CREATE OR REPLACE TABLE issues AS SELECT * FROM df_issues")


print("\n--- All Complex Metrics Saved Successfully ---")
end_time = time.time()
print(f"Berechnungsdauer: {end_time - start_time:.2f} Sekunden")
tables = con.execute("SHOW TABLES").df()
print(tables)
con.close()