import os
import sqlite3
import pandas as pd
from datetime import datetime

def parse_date(date_str):
    if not isinstance(date_str, str):
        return pd.NaT
    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y", "%Y-%m-%d %H:%M:%S"]:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            pass
    return pd.NaT

def clean_service_line(srv):
    if not isinstance(srv, str):
        return "Unknown"
    srv_clean = srv.strip().title()
    srv_clean = srv_clean.replace(" And ", " & ")
    if "Audit" in srv_clean:
        return "Audit & Assurance"
    elif "Tax" in srv_clean:
        return "Tax Advisory"
    elif "Consulting" in srv_clean:
        return "Consulting"
    elif "Risk" in srv_clean:
        return "Risk Advisory"
    elif "Financial" in srv_clean:
        return "Financial Advisory"
    return srv_clean

def run_profitability_etl():
    print("=== STARTING PROFITABILITY ETL PIPELINE ===")
    os.makedirs("data/processed_profitability", exist_ok=True)
    
    df_rev = pd.read_csv("data/raw_profitability/service_revenues.csv")
    df_costs = pd.read_csv("data/raw_profitability/finance_costs.csv")
    
    df_rev["invoice_date_clean"] = df_rev["invoice_date"].apply(parse_date)
    df_rev["service_line_clean"] = df_rev["service_line"].apply(clean_service_line)
    df_costs["service_line_clean"] = df_costs["service_line"].apply(clean_service_line)
    
    # dim_services
    unique_services = sorted(list(df_rev["service_line_clean"].unique()))
    services_dict = {srv: f"SRV_{i+1:02d}" for i, srv in enumerate(unique_services)}
    dim_services = pd.DataFrame([
        {"service_id": sid, "service_line": srv} for srv, sid in services_dict.items()
    ])
    
    # dim_regions
    unique_regions = sorted(list(df_rev["region"].dropna().unique()))
    regions_dict = {reg: f"REG_{i+1:02d}" for i, reg in enumerate(unique_regions)}
    dim_regions = pd.DataFrame([
        {"region_id": rid, "region_name": reg} for reg, rid in regions_dict.items()
    ])
    
    # dim_customer_types
    unique_custs = sorted(list(df_rev["customer_type"].dropna().unique()))
    custs_dict = {c: f"CUST_{i+1:02d}" for i, c in enumerate(unique_custs)}
    dim_customer_types = pd.DataFrame([
        {"cust_type_id": cid, "customer_type": c} for c, cid in custs_dict.items()
    ])
    
    # dim_date
    all_dates = df_rev["invoice_date_clean"].dropna().unique()
    start_date = min(all_dates)
    end_date = max(all_dates)
    date_range = pd.date_range(start=start_date, end=end_date)
    
    dim_date = pd.DataFrame({
        "date_key": date_range.strftime("%Y%m%d").astype(int),
        "date_actual": date_range.strftime("%Y-%m-%d"),
        "month": date_range.strftime("%Y-%m"),
        "year": date_range.year,
        "quarter": date_range.quarter
    })
    
    # fact_revenues
    df_rev["service_id"] = df_rev["service_line_clean"].map(services_dict)
    df_rev["region_id"] = df_rev["region"].map(regions_dict)
    df_rev["cust_type_id"] = df_rev["customer_type"].map(custs_dict)
    df_rev["date_key"] = df_rev["invoice_date_clean"].dt.strftime("%Y%m%d").fillna(0).astype(int)
    
    fact_revenues = df_rev[[
        "invoice_id", "date_key", "service_id", "region_id", "cust_type_id", 
        "revenue_amount", "days_outstanding"
    ]].copy()
    
    # fact_costs
    df_costs["service_id"] = df_costs["service_line_clean"].map(services_dict)
    df_costs["cost_id"] = [f"CST_{i+1:04d}" for i in range(len(df_costs))]
    
    fact_costs = df_costs[[
        "cost_id", "cost_month", "service_id", "labor_costs", "operational_costs", "fixed_overhead"
    ]].copy()
    
    # ExportProcessed
    dim_services.to_csv("data/processed_profitability/dim_services.csv", index=False)
    dim_regions.to_csv("data/processed_profitability/dim_regions.csv", index=False)
    dim_customer_types.to_csv("data/processed_profitability/dim_customer_types.csv", index=False)
    dim_date.to_csv("data/processed_profitability/dim_date.csv", index=False)
    fact_revenues.to_csv("data/processed_profitability/fact_revenues.csv", index=False)
    fact_costs.to_csv("data/processed_profitability/fact_costs.csv", index=False)
    
    # Load SQLite
    db_path = "data/profitability.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE dim_services (
        service_id TEXT PRIMARY KEY,
        service_line TEXT UNIQUE
    )""")
    cursor.execute("""
    CREATE TABLE dim_regions (
        region_id TEXT PRIMARY KEY,
        region_name TEXT UNIQUE
    )""")
    cursor.execute("""
    CREATE TABLE dim_customer_types (
        cust_type_id TEXT PRIMARY KEY,
        customer_type TEXT UNIQUE
    )""")
    cursor.execute("""
    CREATE TABLE dim_date (
        date_key INTEGER PRIMARY KEY,
        date_actual TEXT,
        month TEXT,
        year INTEGER,
        quarter INTEGER
    )""")
    cursor.execute("""
    CREATE TABLE fact_revenues (
        invoice_id TEXT PRIMARY KEY,
        date_key INTEGER,
        service_id TEXT,
        region_id TEXT,
        cust_type_id TEXT,
        revenue_amount REAL,
        days_outstanding INTEGER,
        FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
        FOREIGN KEY (service_id) REFERENCES dim_services(service_id),
        FOREIGN KEY (region_id) REFERENCES dim_regions(region_id),
        FOREIGN KEY (cust_type_id) REFERENCES dim_customer_types(cust_type_id)
    )""")
    cursor.execute("""
    CREATE TABLE fact_costs (
        cost_id TEXT PRIMARY KEY,
        cost_month TEXT,
        service_id TEXT,
        labor_costs REAL,
        operational_costs REAL,
        fixed_overhead REAL,
        FOREIGN KEY (service_id) REFERENCES dim_services(service_id)
    )""")
    
    dim_services.to_sql("dim_services", conn, if_exists="append", index=False)
    dim_regions.to_sql("dim_regions", conn, if_exists="append", index=False)
    dim_customer_types.to_sql("dim_customer_types", conn, if_exists="append", index=False)
    dim_date.to_sql("dim_date", conn, if_exists="append", index=False)
    fact_revenues.to_sql("fact_revenues", conn, if_exists="append", index=False)
    fact_costs.to_sql("fact_costs", conn, if_exists="append", index=False)
    
    cursor.execute("CREATE INDEX idx_rev_service ON fact_revenues(service_id)")
    cursor.execute("CREATE INDEX idx_rev_region ON fact_revenues(region_id)")
    cursor.execute("CREATE INDEX idx_rev_date ON fact_revenues(date_key)")
    cursor.execute("CREATE INDEX idx_costs_service ON fact_costs(service_id)")
    cursor.execute("CREATE INDEX idx_costs_month ON fact_costs(cost_month)")
    
    conn.commit()
    conn.close()
    
    print("[SUCCESS] SQLite database profitability.db created and indexed successfully!")
    print("=== PROFITABILITY ETL PIPELINE COMPLETED SUCCESSFULLY ===")
    return True
