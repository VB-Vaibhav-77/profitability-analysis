import os
import random
import pandas as pd
from datetime import datetime, timedelta

def generate_profitability_data():
    print("Generating simulated Profitability Analysis raw data...")
    os.makedirs("data/raw_profitability", exist_ok=True)
    random.seed(42)
    
    services = ["Audit & Assurance", "Tax Advisory", "Consulting", "Risk Advisory", "Financial Advisory"]
    regions = ["North America", "EMEA", "APAC", "LATAM"]
    customer_types = ["Enterprise", "SME", "Government"]
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
    
    invoices = []
    invoice_formats = ["%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y"]
    
    for i in range(1, 1501):
        inv_date = random.choice(date_range)
        date_format = random.choice(invoice_formats)
        date_str = inv_date.strftime(date_format)
        
        srv = random.choice(services)
        if random.random() < 0.2:
            srv = srv.lower()
        elif random.random() < 0.2:
            srv = srv.upper()
            
        invoices.append({
            "invoice_id": f"INV_{i:04d}",
            "invoice_date": date_str,
            "service_line": srv,
            "region": random.choice(regions),
            "customer_type": random.choice(customer_types),
            "revenue_amount": round(random.uniform(5000, 75000), 2),
            "days_outstanding": random.randint(0, 115)
        })
        
    df_rev = pd.DataFrame(invoices)
    df_rev.to_csv("data/raw_profitability/service_revenues.csv", index=False)
    print(f" -> Generated {len(df_rev)} service invoices in service_revenues.csv")
    
    costs = []
    current_date = start_date
    while current_date <= end_date:
        month_str = current_date.strftime("%Y-%m")
        for srv in services:
            labor = round(random.uniform(25000, 180000), 2)
            ops = round(random.uniform(10000, 60000), 2)
            fixed = round(random.uniform(5000, 25000), 2)
            
            costs.append({
                "cost_month": month_str,
                "service_line": srv,
                "labor_costs": labor,
                "operational_costs": ops,
                "fixed_overhead": fixed
            })
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1)
            
    df_costs = pd.DataFrame(costs)
    df_costs.to_csv("data/raw_profitability/finance_costs.csv", index=False)
    print(f" -> Generated {len(df_costs)} monthly cost logs in finance_costs.csv")
    print("Profitability raw data generation complete!")

if __name__ == "__main__":
    generate_profitability_data()
