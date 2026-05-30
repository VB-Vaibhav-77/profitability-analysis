import sqlite3
import pandas as pd
import os

def run_profitability_sql_analysis():
    print("Running Profitability SQL Analytics Reports...")
    os.makedirs("data/processed_profitability", exist_ok=True)
    
    db_path = "data/profitability.db"
    conn = sqlite3.connect(db_path)
    
    # Gross Profit Margins
    query_service_profit = """
    WITH MonthlyRevenue AS (
        SELECT 
            d.month,
            r.service_id,
            SUM(r.revenue_amount) AS total_revenue
        FROM fact_revenues r
        JOIN dim_date d ON r.date_key = d.date_key
        GROUP BY d.month, r.service_id
    ),
    MonthlyProfit AS (
        SELECT 
            mr.month,
            s.service_line,
            mr.total_revenue,
            (c.labor_costs + c.operational_costs + c.fixed_overhead) AS total_cost
        FROM MonthlyRevenue mr
        JOIN dim_services s ON mr.service_id = s.service_id
        JOIN fact_costs c ON mr.month = c.cost_month AND mr.service_id = c.service_id
    )
    SELECT 
        service_line,
        ROUND(SUM(total_revenue), 2) AS cumulative_revenue,
        ROUND(SUM(total_cost), 2) AS cumulative_cost,
        ROUND(SUM(total_revenue) - SUM(total_cost), 2) AS net_profit,
        ROUND((SUM(total_revenue) - SUM(total_cost)) / SUM(total_revenue) * 100, 2) AS profit_margin_pct
    FROM MonthlyProfit
    GROUP BY service_line
    ORDER BY net_profit DESC
    """
    df_service = pd.read_sql_query(query_service_profit, conn)
    df_service.to_csv("data/processed_profitability/service_profit_report.csv", index=False)
    print(" -> Service Profit Report compiled successfully.")
    
    # MoM Variance
    query_mom = """
    WITH MonthlyRevenue AS (
        SELECT 
            d.month,
            SUM(r.revenue_amount) AS total_revenue
        FROM fact_revenues r
        JOIN dim_date d ON r.date_key = d.date_key
        GROUP BY d.month
    ),
    MonthlyCost AS (
        SELECT 
            cost_month AS month,
            SUM(labor_costs + operational_costs + fixed_overhead) AS total_cost
        FROM fact_costs
        GROUP BY cost_month
    ),
    MonthlySummary AS (
        SELECT 
            mr.month,
            mr.total_revenue,
            mc.total_cost,
            (mr.total_revenue - mc.total_cost) AS monthly_profit
        FROM MonthlyRevenue mr
        JOIN MonthlyCost mc ON mr.month = mc.month
    )
    SELECT 
        month,
        ROUND(total_revenue, 2) AS total_revenue,
        ROUND(total_cost, 2) AS total_cost,
        ROUND(monthly_profit, 2) AS monthly_profit,
        ROUND(LAG(monthly_profit, 1) OVER (ORDER BY month), 2) AS prev_month_profit,
        ROUND((monthly_profit - LAG(monthly_profit, 1) OVER (ORDER BY month)) / LAG(monthly_profit, 1) OVER (ORDER BY month) * 100, 2) AS mom_variance_pct
    FROM MonthlySummary
    """
    df_mom = pd.read_sql_query(query_mom, conn)
    df_mom.to_csv("data/processed_profitability/mom_profit_trends.csv", index=False)
    print(" -> Monthly MoM Trends compiled successfully.")
    
    # Regional
    query_region = """
    SELECT 
        reg.region_name,
        cust.customer_type,
        ROUND(SUM(r.revenue_amount), 2) AS total_revenue,
        ROUND(AVG(r.days_outstanding), 1) AS avg_days_outstanding
    FROM fact_revenues r
    JOIN dim_regions reg ON r.region_id = reg.region_id
    JOIN dim_customer_types cust ON r.cust_type_id = cust.cust_type_id
    GROUP BY reg.region_name, cust.customer_type
    ORDER BY total_revenue DESC
    """
    df_region = pd.read_sql_query(query_region, conn)
    df_region.to_csv("data/processed_profitability/regional_customer_performance.csv", index=False)
    print(" -> Regional Segmentation Report compiled successfully.")
    
    conn.close()
    return True
