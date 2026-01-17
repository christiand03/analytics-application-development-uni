import pandas as pd
import duckdb
import time
import metrics as mt
import os
import data_cleaning as dc

DB_DIR = "resources"
DB_NAME = "dashboard_data.duckdb"
DB_OLD_NAME = "dashboard_data_old.duckdb"

DB_PATH = os.path.join(DB_DIR, DB_NAME)
DB_OLD_PATH = os.path.join(DB_DIR, DB_OLD_NAME)

print("--- Step 0: Database Rotation ---")
if os.path.exists(DB_OLD_PATH):
    try:
        os.remove(DB_OLD_PATH)
        print(f"Old backup deleted: {DB_OLD_PATH}")
    except PermissionError:
        print(f"WARNING: Could not delete {DB_OLD_PATH}. File might be open?")

if os.path.exists(DB_PATH):
    try:
        os.rename(DB_PATH, DB_OLD_PATH)
        print(f"Existing DB moved to: {DB_OLD_PATH}")
    except PermissionError:
        print(f"WARNING: Could not move {DB_PATH}. File might be open?")

start_time = time.time()

print("--- Step 1: Loading Data ---")
auftragsdaten, positionsdaten, zeitdaten = dc.load_data()

print("--- Step 2: Merging & Cleaning ---")
df, df2 = dc.data_cleaning(auftragsdaten, positionsdaten, zeitdaten)


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
empty_orders_count = mt.empty_orders(df)

# --- 2. Data Quality (Nulls & Uniqueness) ---
# returns: (float, DataFrame) -> ignore the Dataframe (_)
null_ratio_orders, _ = mt.data_cleanliness(df, group_by_col=None)
null_ratio_positions, _ = mt.data_cleanliness(df2, group_by_col=None)
unique_kva, unique_pos = mt.uniqueness_check(df, df2)

# --- 3. Business Logic / Test Data ---
test_data_count = mt.Kundengruppe_containing_test(df, return_frame=False)

# --- 4. Plausibility Checks (Tuples extraction) ---
# returns: (DataFrame, count, avg) -> ignore the DataFrame (_)
_, plausibility_error_count_df, plausibility_avg_diff_df = mt.plausibilitaetscheck_forderung_einigung(df)
_, plausibility_error_count_df2, plausibility_avg_diff_df2 = mt.plausibilitaetscheck_forderung_einigung(df2)

# returns: (DataFrame, count) -> ignore the DataFrame (_)
_, proforma_count = mt.proformabelege(df)

# --- 5. Logic Errors ---
discount_logic_errors = mt.discount_check(df2)



print("--- Step 5: Constructing Scalar Metrics Table ---")

kpi_data = {
    # General
    'count_total_orders': [total_orders],
    'count_total_positions': [total_positions],
    'count_empty_orders': [empty_orders_count],

    # Quality
    'null_row_ratio_orders': [null_ratio_orders],
    'null_row_ratio_positions': [null_ratio_positions],
    'is_unique_kva_id': [unique_kva],
    'is_unique_position_id': [unique_pos],

    # Test Data
    'count_test_data_rows': [test_data_count],

    # Logic Errors
    'count_plausibility_errors_df': [plausibility_error_count_df],
    'avg_plausibility_diff_df': [plausibility_avg_diff_df],
    'count_plausibility_errors_df2': [plausibility_error_count_df2],
    'avg_plausibility_diff_df2': [plausibility_avg_diff_df2],
    'count_proforma_receipts': [proforma_count],
    'count_discount_logic_errors': [discount_logic_errors],
}

df_scalars = pd.DataFrame(kpi_data)

print("--- Step 6: Saving to DuckDB ---")
con.execute("CREATE OR REPLACE TABLE scalar_metrics AS SELECT * FROM df_scalars")



print("--- Step 7: Computing Complex Metrics and Creating Tables ---")

# Null Ratios per Column (Returns DataFrame)
print("1. Null Ratios")
df_null_ratios = mt.ratio_null_values_column(df)
con.execute("CREATE OR REPLACE TABLE metric_null_ratios_per_column AS SELECT * FROM df_null_ratios")

# Test Data Entries (Returns (int, DataFrame) -> we want the DF)
print("2. Test Data Check")
df_test_rows = mt.Kundengruppe_containing_test(df, return_frame=True)
con.execute("CREATE OR REPLACE TABLE metric_test_data_entries AS SELECT * FROM df_test_rows")

# Plausibility Check (Returns (DataFrame, int, avg) -> only extract the DataFrame)
print("3. Plausibility Differences")
df_plausi_df, _, _ = mt.plausibilitaetscheck_forderung_einigung(df)
con.execute("CREATE OR REPLACE TABLE metric_plausibility_diffs_auftragsdaten AS SELECT * FROM df_plausi_df")

df_plausi_df2, _, _ = mt.plausibilitaetscheck_forderung_einigung(df2)
con.execute("CREATE OR REPLACE TABLE metric_plausibility_diffs_positionsdaten AS SELECT * FROM df_plausi_df2")

# Data Cleanliness Grouped (Returns (Series, DataFrame))
print("4. Data Cleanliness Grouped")
series_row_ratios_grouped_df, df_col_ratios_grouped_df = mt.data_cleanliness(df, group_by_col="Kundengruppe")

# Reset index to make 'Kundengruppe' a real column
con.execute("CREATE OR REPLACE TABLE metric_cleanliness_cols_grouped_auftragsdaten AS SELECT * FROM df_col_ratios_grouped_df")

# Handle the Series part (Rows)
df_clean_rows_df = series_row_ratios_grouped_df.to_frame(name='row_null_ratio').reset_index()
con.execute("CREATE OR REPLACE TABLE metric_cleanliness_rows_grouped_auftragsdaten AS SELECT * FROM df_clean_rows_df")


print("5. Data Cleanliness Ungrouped")
_, df_col_ratios_ungrouped_df = mt.data_cleanliness(df, group_by_col=None)
df_col_ratios_ungrouped_df = df_col_ratios_ungrouped_df.rename(columns={'index': 'column_name'})
con.execute("CREATE OR REPLACE TABLE metric_cleanliness_cols_ungrouped_auftragsdaten AS SELECT * FROM df_col_ratios_ungrouped_df")

_, df_col_ratios_ungrouped_df2 = mt.data_cleanliness(df2, group_by_col=None)
df_col_ratios_ungrouped_df2 = df_col_ratios_ungrouped_df2.rename(columns={'index': 'column_name'})
con.execute("CREATE OR REPLACE TABLE metric_cleanliness_cols_ungrouped_positionsdaten AS SELECT * FROM df_col_ratios_ungrouped_df2")


# Proforma Receipts Returns (DataFrame, int)
print("6. Proforma Receipts")
df_proforma, _ = mt.proformabelege(df)
con.execute("CREATE OR REPLACE TABLE metric_proforma AS SELECT * FROM df_proforma")

# High Value > 50k (Returns DataFrame)
print("7. Suspiciously high Value")
df_above_50k = mt.above_50k(df)
con.execute("CREATE OR REPLACE TABLE metric_above_50k AS SELECT * FROM df_above_50k")

# Zeitwert Errors (Returns Series -> Convert to DF)
print("8. Zeitwert Errors")
zeitwert = mt.check_zeitwert(df)
#df_zeitwert = zeitwert.to_frame(name='zeitwert_diff')
con.execute("CREATE OR REPLACE TABLE metric_zeitwert_errors AS SELECT * FROM zeitwert")

# Positions over Time (Returns DataFrame)
print("9. Positions Over Time")
df_pos_time = mt.positions_per_order_over_time(df, df2, time_col="CRMEingangszeit")
con.execute("CREATE OR REPLACE TABLE metric_positions_over_time AS SELECT * FROM df_pos_time")

# Error Frequency Heatmap (Returns DataFrame)
print("10. Error Frequency Heatmap")
df_heatmap = mt.error_frequency_by_weekday_hour(df, time_col="CRMEingangszeit")
con.execute("CREATE OR REPLACE TABLE metric_error_heatmap AS SELECT * FROM df_heatmap")

# Order vs Position Financial Mismatch (Returns DataFrame)
print("11. Order/Position Mismatch")
df_mismatch = mt.abgleich_auftraege(df, df2)
con.execute("CREATE OR REPLACE TABLE metric_order_pos_mismatch AS SELECT * FROM df_mismatch")

# Handwerker Outliers (Returns DataFrame)
print("12. Handwerker Outliers")
df_outlier = mt.handwerker_gewerke_outlier(df)
df_outliers_true = df_outlier[df_outlier['is_outlier'] == True].copy()
df_outliers_true['Check_Result'] = mt.check_keywords(df_outliers_true)
con.execute("CREATE OR REPLACE TABLE metric_handwerker_outliers AS SELECT * FROM df_outliers_true")

# Semantic Handwerker Mismatches (Returns DataFrame)
print("13. Semantic Handwerker Mismatches")
df_semantic = mt.mismatched_entries(df)
con.execute("CREATE OR REPLACE TABLE metric_semantic_mismatches AS SELECT * FROM df_semantic")

# Optional: Leere Tabelle in DB anlegen, falls mt.get_mismatched_entries(df) nicht ausgeführt werden kann
#df_semantic = []
#con.execute("CREATE OR REPLACE TABLE metric_semantic_mismatches AS SELECT 'dummy' as col1 WHERE 1=0")

print("14. Calculate Position count")
position_count_df2 = mt.position_count(df2)
con.execute("CREATE OR REPLACE TABLE metric_position_count_positionsdaten AS SELECT * FROM position_count_df2")

print("Calculating Extended Chart Data...")
# page4 Tab 2
disc_stats, disc_details = mt.discount_details(df2)
con.execute("CREATE OR REPLACE TABLE metric_discount_stats AS SELECT * FROM disc_stats")
con.execute("CREATE OR REPLACE TABLE metric_discount_details AS SELECT * FROM disc_details")

# page4 Tab 4
fn_stats1, fn_details1 = mt.false_negative_df1(df)
con.execute("CREATE OR REPLACE TABLE metric_fn_stats_df1 AS SELECT * FROM fn_stats1")
con.execute("CREATE OR REPLACE TABLE metric_fn_details_df1 AS SELECT * FROM fn_details1")

# page4 Tab 5
fn_stats2, fn_details2 = mt.false_negative_df2(df2)
con.execute("CREATE OR REPLACE TABLE metric_fn_stats_df2 AS SELECT * FROM fn_stats2")
con.execute("CREATE OR REPLACE TABLE metric_fn_details_df2 AS SELECT * FROM fn_details2")

print("--- Step 8: Calculating overall Issue Metric ---")
numeric_issues = len(zeitwert) + len(df_above_50k) + len(df_mismatch)
text_issues = test_data_count + len(df_outliers_true) + len(df_semantic)
plausi_issues = plausibility_error_count_df + plausibility_error_count_df2 + discount_logic_errors + proforma_count + len(fn_details1) + len(fn_details2)
overall_issues = numeric_issues + text_issues + plausi_issues

issues = {
    'numeric_issues': [numeric_issues],
    'text_issues': [text_issues],
    'plausi_issues': [plausi_issues],
    'overall_issues': [overall_issues],
    'count_zeitwert_errors': [len(zeitwert)],
    'count_above_50k': [len(df_above_50k)],
    'count_handwerker_outliers': [len(df_outliers_true)],
    'count_semantic_outliers': [len(df_semantic)],
    'count_abweichung_summen': [len(df_mismatch)],
    'count_plausibility_errors_df': [plausibility_error_count_df],
    'count_plausibility_errors_df2': [plausibility_error_count_df2],
    'count_false_negative_df': [len(fn_details1)],
    'count_false_negative_df2': [len(fn_details2)],
}

df_issues = pd.DataFrame(issues)
print(df_issues)
con.execute("CREATE OR REPLACE TABLE issues AS SELECT * FROM df_issues")


print("--- Step 9: Comparing with Old Database (Metric Trends) ---")

df_new_combined = pd.concat([df_scalars, df_issues], axis=1)
df_comparison = df_new_combined.T.reset_index()
df_comparison.columns = ['Metric', 'Current_Value']

df_old_combined = pd.DataFrame()

if os.path.exists(DB_OLD_PATH):
    try:
        con_old = duckdb.connect(DB_OLD_PATH, read_only=True)

        tables_old = con_old.execute("SHOW TABLES").df()['name'].tolist()

        old_scalars = pd.DataFrame()
        old_issues = pd.DataFrame()

        if 'scalar_metrics' in tables_old:
            old_scalars = con_old.execute("SELECT * FROM scalar_metrics").df()

        if 'issues' in tables_old:
            old_issues = con_old.execute("SELECT * FROM issues").df()

        con_old.close()

        if not old_scalars.empty or not old_issues.empty:
            df_old_combined = pd.concat([old_scalars, old_issues], axis=1)

    except Exception as e:
        print(f"WARNING: Can not read old database: {e}")
else:
    print("No old database found (first run?). Comparison values are 0.")


if not df_old_combined.empty:
    df_old_long = df_old_combined.T.reset_index()
    df_old_long.columns = ['Metric', 'Old_Value']

    df_comparison = pd.merge(df_comparison, df_old_long, on='Metric', how='left')

    df_comparison['Old_Value'] = df_comparison['Old_Value'].fillna(0)

else:
    df_comparison['Old_Value'] = 0.0

df_comparison['Current_Value'] = pd.to_numeric(df_comparison['Current_Value'], errors='coerce').fillna(0)
df_comparison['Old_Value'] = pd.to_numeric(df_comparison['Old_Value'], errors='coerce').fillna(0)

df_comparison['Absolute_Change'] = df_comparison['Current_Value'] - df_comparison['Old_Value']

def calc_percent(row):
    old = row['Old_Value']
    new = row['Current_Value']
    diff = row['Absolute_Change']

    if old == 0:
        if new == 0:
            return 0.0
        else:
            return 100.0

    return (diff / old) * 100

df_comparison['Percent_Change'] = df_comparison.apply(calc_percent, axis=1).round(2)

df_comparison = df_comparison.sort_values('Metric')

print("Comparison table created:")
print(df_comparison[['Metric', 'Current_Value', 'Old_Value', 'Percent_Change']].head())

con.execute("CREATE OR REPLACE TABLE metric_comparison AS SELECT * FROM df_comparison")


print("\n--- All Complex Metrics Saved Successfully ---")
end_time = time.time()
print(f"Berechnungsdauer: {end_time - start_time:.2f} Sekunden")
tables = con.execute("SHOW TABLES").df()
print(tables)
con.close()

# Optional: Aufräumen der alten Datenbank nach erfolgreicher Erstellung der neuen
# print("--- Step 10: Cleaning up ---")
# if os.path.exists(DB_OLD_PATH):
#     try:
#         os.remove(DB_OLD_PATH)
#         print(f"Old backup deleted: {DB_OLD_PATH}")
#     except Exception as e:
#         print(f"WARNING: Could not delete old database: {e}")