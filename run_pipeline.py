import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PROFITABILITY_PIPELINE")

from src.generate_data import generate_profitability_data
from src.etl import run_profitability_etl
from src.sql_queries import run_profitability_sql_analysis

def main():
    logger.info("================================================================")
    logger.info("         [B2B CORPORATE SERVICE PROFITABILITY PIPELINE]         ")
    logger.info("================================================================")
    
    logger.info("--- STEP 1: GENERATING FINANCIAL SHEET DATA ---")
    generate_profitability_data()
    
    logger.info("\n--- STEP 2: RUNNING ETL TRANSFORMATIONS ---")
    if not run_profitability_etl():
        logger.error("ETL failed.")
        sys.exit(1)
        
    logger.info("\n--- STEP 3: EXECUTING SQL ANALYTICAL CTE REPORTS ---")
    if not run_profitability_sql_analysis():
        logger.error("SQL Analysis failed.")
        sys.exit(1)
        
    logger.info("================================================================")
    logger.info("[SUCCESS] PIPELINE EXECUTION COMPLETED!")
    logger.info("Relational database saved at: data/profitability.db")
    logger.info("Clean Star Schema CSVs exported to: data/processed_profitability/")
    logger.info("================================================================")

if __name__ == "__main__":
    main()
