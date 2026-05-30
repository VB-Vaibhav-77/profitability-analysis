-- Regional and Customer billing segmentation query
SELECT 
    reg.region_name,
    cust.customer_type,
    ROUND(SUM(r.revenue_amount), 2) AS total_revenue,
    ROUND(AVG(r.days_outstanding), 1) AS avg_days_outstanding
FROM fact_revenues r
JOIN dim_regions reg ON r.region_id = reg.region_id
JOIN dim_customer_types cust ON r.cust_type_id = cust.cust_type_id
GROUP BY reg.region_name, cust.customer_type
ORDER BY total_revenue DESC;
