import os
import sqlite3
import pandas as pd
import pytest
from datetime import datetime
from src.etl.etl_pipeline import parse_date, clean_service_line, run_profitability_etl
from src.data_generator.generate_raw_data import generate_profitability_data
from src.etl.db_loader import load_database
from src.etl.data_validation import ProfitabilityValidator

def test_parse_date_flexible():
    assert parse_date("2024-01-15") == datetime(2024, 1, 15)
    assert parse_date("15/01/2024") == datetime(2024, 1, 15)
    assert pd.isna(parse_date(None))

def test_clean_service_line():
    assert clean_service_line("audit & assurance") == "Audit & Assurance"
    assert clean_service_line("consulting") == "Consulting"

def test_profitability_pipeline():
    generate_profitability_data()
    assert run_profitability_etl() is True
    assert load_database() is True
    
    # Run quality validation
    validator = ProfitabilityValidator()
    assert validator.run_validations() is True
    
    db_path = "data/profitability.db"
    assert os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fact_revenues")
    assert cursor.fetchone()[0] == 1500
    conn.close()
