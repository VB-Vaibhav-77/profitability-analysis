import os
import sqlite3
import pandas as pd
import pytest
from datetime import datetime
from src.etl import parse_date, clean_service_line, run_profitability_etl
from src.generate_data import generate_profitability_data

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
    
    db_path = "data/profitability.db"
    assert os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fact_revenues")
    assert cursor.fetchone()[0] == 1500
    conn.close()
