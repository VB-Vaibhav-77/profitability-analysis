import os
import sqlite3
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Profitability_Validator")

class ProfitabilityValidator:
    def __init__(self, db_path="data/profitability.db"):
        self.db_path = db_path
        
    def run_validations(self):
        logger.info("Starting Profitability Database 20-Point Quality Validation...")
        
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found at {self.db_path}!")
            
        conn = sqlite3.connect(self.db_path)
        all_passed = True
        
        def check_result(test_name, condition, details):
            status = "PASSED" if condition else "FAILED"
            logger.info(f" -> [{test_name}]: {status} - {details}")
            return condition

        # 1. Null Primary Keys Checks
        pk_queries = {
            "dim_services.service_id": "SELECT COUNT(*) FROM dim_services WHERE service_id IS NULL",
            "dim_regions.region_id": "SELECT COUNT(*) FROM dim_regions WHERE region_id IS NULL",
            "dim_customer_types.cust_type_id": "SELECT COUNT(*) FROM dim_customer_types WHERE cust_type_id IS NULL",
            "dim_date.date_key": "SELECT COUNT(*) FROM dim_date WHERE date_key IS NULL",
            "fact_revenues.invoice_id": "SELECT COUNT(*) FROM fact_revenues WHERE invoice_id IS NULL",
            "fact_costs.cost_id": "SELECT COUNT(*) FROM fact_costs WHERE cost_id IS NULL"
        }
        for field, q in pk_queries.items():
            count = pd.read_sql_query(q, conn).iloc[0, 0]
            if not check_result(f"Null Check: {field}", count == 0, f"Found {count} null IDs."):
                all_passed = False

        # 2. Key Uniqueness Checks
        uq_queries = {
            "dim_services.service_id": "SELECT COUNT(service_id) - COUNT(DISTINCT service_id) FROM dim_services",
            "dim_regions.region_id": "SELECT COUNT(region_id) - COUNT(DISTINCT region_id) FROM dim_regions",
            "dim_customer_types.cust_type_id": "SELECT COUNT(cust_type_id) - COUNT(DISTINCT cust_type_id) FROM dim_customer_types",
            "dim_date.date_key": "SELECT COUNT(date_key) - COUNT(DISTINCT date_key) FROM dim_date",
            "fact_revenues.invoice_id": "SELECT COUNT(invoice_id) - COUNT(DISTINCT invoice_id) FROM fact_revenues",
            "fact_costs.cost_id": "SELECT COUNT(cost_id) - COUNT(DISTINCT cost_id) FROM fact_costs"
        }
        for field, q in uq_queries.items():
            dups = pd.read_sql_query(q, conn).iloc[0, 0]
            if not check_result(f"Uniqueness Check: {field}", dups == 0, f"Found {dups} duplicate primary keys."):
                all_passed = False

        # 3. Value Constraints Bounds Checks
        neg_val_queries = {
            "fact_revenues.revenue_amount": "SELECT COUNT(*) FROM fact_revenues WHERE revenue_amount <= 0",
            "fact_costs.labor_costs": "SELECT COUNT(*) FROM fact_costs WHERE labor_costs < 0",
            "fact_costs.operational_costs": "SELECT COUNT(*) FROM fact_costs WHERE operational_costs < 0",
            "fact_costs.fixed_overhead": "SELECT COUNT(*) FROM fact_costs WHERE fixed_overhead < 0",
            "fact_revenues.days_outstanding": "SELECT COUNT(*) FROM fact_revenues WHERE days_outstanding < 0"
        }
        for field, q in neg_val_queries.items():
            violations = pd.read_sql_query(q, conn).iloc[0, 0]
            if not check_result(f"Value Bounds: {field}", violations == 0, f"Found {violations} negative boundaries."):
                all_passed = False

        # 4. Referential Integrity Mappings Checks
        ref_queries = {
            "fact_revenues -> dim_services": "SELECT COUNT(*) FROM fact_revenues WHERE service_id NOT IN (SELECT service_id FROM dim_services)",
            "fact_revenues -> dim_regions": "SELECT COUNT(*) FROM fact_revenues WHERE region_id NOT IN (SELECT region_id FROM dim_regions)",
            "fact_costs -> dim_services": "SELECT COUNT(*) FROM fact_costs WHERE service_id NOT IN (SELECT service_id FROM dim_services)"
        }
        for relationship, q in ref_queries.items():
            orphans = pd.read_sql_query(q, conn).iloc[0, 0]
            if not check_result(f"Ref Integrity: {relationship}", orphans == 0, f"Found {orphans} orphaned records."):
                all_passed = False

        conn.close()
        logger.info(f"=== DB QUALITY VALIDATION COMPLETED: {'PASSED' if all_passed else 'FAILED'} ===")
        return all_passed
