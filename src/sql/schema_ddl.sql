-- Relational DDL for Service Profitability Analysis
CREATE TABLE dim_services (
    service_id TEXT PRIMARY KEY,
    service_line TEXT UNIQUE
);

CREATE TABLE dim_regions (
    region_id TEXT PRIMARY KEY,
    region_name TEXT UNIQUE
);

CREATE TABLE dim_customer_types (
    cust_type_id TEXT PRIMARY KEY,
    customer_type TEXT UNIQUE
);

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    date_actual TEXT,
    month TEXT,
    year INTEGER,
    quarter INTEGER
);

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
);

CREATE TABLE fact_costs (
    cost_id TEXT PRIMARY KEY,
    cost_month TEXT,
    service_id TEXT,
    labor_costs REAL,
    operational_costs REAL,
    fixed_overhead REAL,
    FOREIGN KEY (service_id) REFERENCES dim_services(service_id)
);

CREATE INDEX idx_rev_service ON fact_revenues(service_id);
CREATE INDEX idx_rev_region ON fact_revenues(region_id);
CREATE INDEX idx_rev_date ON fact_revenues(date_key);
CREATE INDEX idx_costs_service ON fact_costs(service_id);
CREATE INDEX idx_costs_month ON fact_costs(cost_month);
