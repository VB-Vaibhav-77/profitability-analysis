-- Monthly profit variance with window LAG functions
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
FROM MonthlySummary;
