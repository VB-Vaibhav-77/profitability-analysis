import sqlite3
import pandas as pd
import os

def load_database():
    print("Compiling SQLite Database at data/profitability.db...")
    db_path = "data/profitability.db"
    
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read DDL schema file
    ddl_path = "src/sql/schema_ddl.sql"
    with open(ddl_path, "r") as f:
        ddl_sql = f.read()
        
    cursor.executescript(ddl_sql)
    
    # Read processed CSVs and insert
    dim_services = pd.read_csv("data/processed/dim_services.csv")
    dim_regions = pd.read_csv("data/processed/dim_regions.csv")
    dim_customer_types = pd.read_csv("data/processed/dim_customer_types.csv")
    dim_date = pd.read_csv("data/processed/dim_date.csv")
    fact_revenues = pd.read_csv("data/processed/fact_revenues.csv")
    fact_costs = pd.read_csv("data/processed/fact_costs.csv")
    
    dim_services.to_sql("dim_services", conn, if_exists="append", index=False)
    dim_regions.to_sql("dim_regions", conn, if_exists="append", index=False)
    dim_customer_types.to_sql("dim_customer_types", conn, if_exists="append", index=False)
    dim_date.to_sql("dim_date", conn, if_exists="append", index=False)
    fact_revenues.to_sql("fact_revenues", conn, if_exists="append", index=False)
    fact_costs.to_sql("fact_costs", conn, if_exists="append", index=False)
    
    conn.commit()
    conn.close()
    print("[SUCCESS] Relational SQLite Database loaded and indexed successfully!")
    return True
