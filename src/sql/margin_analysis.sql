-- Service Line Gross Profit margins query
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
ORDER BY net_profit DESC;
