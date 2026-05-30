import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("APEX_PROFITABILITY_MASTER")

from src.data_generator.generate_raw_data import generate_profitability_data
from src.etl.etl_pipeline import run_profitability_etl
from src.etl.db_loader import load_database
from src.etl.data_validation import ProfitabilityValidator
import sqlite3
import pandas as pd

def main():
    logger.info("=====================================================================")
    logger.info("         APEXANALYTICS: CORPORATE SERVICE PROFITABILITY PIPELINE     ")
    logger.info("=====================================================================")
    
    # 1. Simulate data
    logger.info("--- Phase 1: Generating Raw Spreadsheets Cost Sheets ---")
    generate_profitability_data()
    
    # 2. Run ETL
    logger.info("\n--- Phase 2: Standardizing Service Casing and Date Formats ---")
    if not run_profitability_etl():
        logger.error("ETL failed.")
        sys.exit(1)
        
    # 3. Load DB
    logger.info("\n--- Phase 3: Building Relational Indices and Loading Database ---")
    if not load_database():
        logger.error("Database Loader failed.")
        sys.exit(1)
        
    # 4. Validate DB
    logger.info("\n--- Phase 4: Executing 20-Point QA Constraint Suite ---")
    validator = ProfitabilityValidator()
    if not validator.run_validations():
        logger.error("Database Quality suite failed. Integrity constraints broken!")
        sys.exit(1)
        
    # 5. SQL Reports
    logger.info("\n--- Phase 5: Executing SQL Analytics CTE Reports ---")
    conn = sqlite3.connect("data/profitability.db")
    
    # Gross Margin CTE
    with open("src/sql/margin_analysis.sql", "r") as f:
        df_margin = pd.read_sql_query(f.read(), conn)
    df_margin.to_csv("data/processed/service_profit_report.csv", index=False)
    logger.info(" -> margin_analysis.sql compiled and saved successfully.")
    
    # MoM Growth CTE
    with open("src/sql/mom_variance.sql", "r") as f:
        df_mom = pd.read_sql_query(f.read(), conn)
    df_mom.to_csv("data/processed/mom_profit_trends.csv", index=False)
    logger.info(" -> mom_variance.sql compiled and saved successfully.")
    
    # Regional CTE
    with open("src/sql/regional_segmentation.sql", "r") as f:
        df_reg = pd.read_sql_query(f.read(), conn)
    df_reg.to_csv("data/processed/regional_customer_performance.csv", index=False)
    logger.info(" -> regional_segmentation.sql compiled and saved successfully.")
    
    conn.close()
    
    logger.info("=====================================================================")
    logger.info("[SUCCESS] PIPELINE BUILD FINISHED SUCCESSFULLY!")
    logger.info("Prisine database compiled at: data/profitability.db")
    logger.info("Analytical outputs exported to: data/processed/")
    logger.info("=====================================================================")

if __name__ == "__main__":
    main()
