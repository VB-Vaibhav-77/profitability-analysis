import os
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
    os.makedirs("data/processed", exist_ok=True)
    
    df_rev = pd.read_csv("data/raw/service_revenues.csv")
    df_costs = pd.read_csv("data/raw/finance_costs.csv")
    
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
    
    # Export processed schemas
    dim_services.to_csv("data/processed/dim_services.csv", index=False)
    dim_regions.to_csv("data/processed/dim_regions.csv", index=False)
    dim_customer_types.to_csv("data/processed/dim_customer_types.csv", index=False)
    dim_date.to_csv("data/processed/dim_date.csv", index=False)
    fact_revenues.to_csv("data/processed/fact_revenues.csv", index=False)
    fact_costs.to_csv("data/processed/fact_costs.csv", index=False)
    
    print("=== PROFITABILITY ETL PIPELINE TRANSFORMED SUCCESSFULLY ===")
    return True
