# Relational Operational Walkthrough: B2B Corporate Service Profitability Analysis

This playbook documents the local build execution logs and test suites for the premium profitability warehouse.

---

## 🧪 Pipeline Build Execution Stream (`python main.py`)
```text
2026-05-30 21:01:24,426 [INFO] =====================================================================
2026-05-30 21:01:24,426 [INFO]          APEXANALYTICS: CORPORATE SERVICE PROFITABILITY PIPELINE     
2026-05-30 21:01:24,426 [INFO] =====================================================================
2026-05-30 21:01:24,427 [INFO] --- Phase 1: Generating Raw Spreadsheets Cost Sheets ---
Generating simulated Profitability Analysis raw data...
 -> Generated 1500 service invoices in service_revenues.csv
 -> Generated 120 monthly cost logs in finance_costs.csv
Profitability raw data generation complete!

2026-05-30 21:01:24,487 [INFO] --- Phase 2: Standardizing Service Casing and Date Formats ---
=== STARTING PROFITABILITY ETL PIPELINE ===
=== PROFITABILITY ETL PIPELINE TRANSFORMED SUCCESSFULLY ===

2026-05-30 21:01:24,854 [INFO] --- Phase 3: Building Relational Indices and Loading Database ---
Compiling SQLite Database at data/profitability.db...
[SUCCESS] Relational SQLite Database loaded and indexed successfully!

2026-05-30 21:01:24,887 [INFO] --- Phase 4: Executing 20-Point QA Constraint Suite ---
Starting Profitability Database 20-Point Quality Validation...
 -> [Null Check: dim_services.service_id]: PASSED - Found 0 null IDs.
 -> [Null Check: dim_regions.region_id]: PASSED - Found 0 null IDs.
 -> [Null Check: dim_customer_types.cust_type_id]: PASSED - Found 0 null IDs.
 -> [Null Check: dim_date.date_key]: PASSED - Found 0 null IDs.
 -> [Null Check: fact_revenues.invoice_id]: PASSED - Found 0 null IDs.
 -> [Null Check: fact_costs.cost_id]: PASSED - Found 0 null IDs.
 -> [Uniqueness Check: dim_services.service_id]: PASSED - Found 0 duplicate primary keys.
 -> [Uniqueness Check: dim_regions.region_id]: PASSED - Found 0 duplicate primary keys.
 -> [Uniqueness Check: dim_customer_types.cust_type_id]: PASSED - Found 0 duplicate primary keys.
 -> [Uniqueness Check: dim_date.date_key]: PASSED - Found 0 duplicate primary keys.
 -> [Uniqueness Check: fact_revenues.invoice_id]: PASSED - Found 0 duplicate primary keys.
 -> [Uniqueness Check: fact_costs.cost_id]: PASSED - Found 0 duplicate primary keys.
 -> [Value Bounds: fact_revenues.revenue_amount]: PASSED - Found 0 negative boundaries.
 -> [Value Bounds: fact_costs.labor_costs]: PASSED - Found 0 negative boundaries.
 -> [Value Bounds: fact_costs.operational_costs]: PASSED - Found 0 negative boundaries.
 -> [Value Bounds: fact_costs.fixed_overhead]: PASSED - Found 0 negative boundaries.
 -> [Value Bounds: fact_revenues.days_outstanding]: PASSED - Found 0 negative boundaries.
 -> [Ref Integrity: fact_revenues -> dim_services]: PASSED - Found 0 orphaned records.
 -> [Ref Integrity: fact_revenues -> dim_regions]: PASSED - Found 0 orphaned records.
 -> [Ref Integrity: fact_costs -> dim_services]: PASSED - Found 0 orphaned records.
=== DB QUALITY VALIDATION COMPLETED: PASSED ===

2026-05-30 21:01:24,950 [INFO] --- Phase 5: Executing SQL Analytics CTE Reports ---
 -> margin_analysis.sql compiled and saved successfully.
 -> mom_variance.sql compiled and saved successfully.
 -> regional_segmentation.sql compiled and saved successfully.
=====================================================================
[SUCCESS] PIPELINE BUILD FINISHED SUCCESSFULLY!
Prisine database compiled at: data/profitability.db
Analytical outputs exported to: data/processed/
=====================================================================
```

---

## 🧪 Automated Pytest Test Suite (`python -m pytest tests/ -v`)
```text
platform win32 -- Python 3.14.5, pytest-9.0.3 -- C:\Users\vaibh\AppData\Local\Python\pythoncore-3.14-64\python.exe
collected 3 items

tests/test_etl.py::test_parse_date_flexible PASSED                  [ 33%]
tests/test_etl.py::test_clean_service_line PASSED                   [ 66%]
tests/test_etl.py::test_profitability_pipeline PASSED               [100%]

============================== 3 passed in 2.21s ==============================
```
