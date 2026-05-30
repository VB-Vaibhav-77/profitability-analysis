# Power BI Playbook: B2B Corporate Service Profitability Analysis

This playbook defines the exact modeling layout, DAX measure calculations, and visual design guidelines. **No placeholder images are used.**

---

## 🎨 Design Tokens & UI Styles
* **Dashboard Theme**: Sleek Minimalist Dark Slate
* **Color Palette**:
  * **Slate Background**: `#0F172A`
  * **Card Glassmorphism**: `#1E293B` (with 15% opacity)
  * **Primary Metric (Revenue)**: `#38BDF8` (Electric Blue)
  * **Secondary Metric (Margin)**: `#34D399` (Emerald Green)
  * **Alert Text (Low Margin)**: `#FB7185` (Coral Rose)
* **Typography**: Modern sans-serif (e.g., *Inter* or *Segoe UI*)

---

## 🏗️ Star Schema Model Relationships
* **`fact_revenues`** (Fact) ➡️ joined to **`dim_services`** on `service_id` (1-to-many, Single cross-filtering direction)
* **`fact_revenues`** (Fact) ➡️ joined to **`dim_regions`** on `region_id` (1-to-many, Single cross-filtering direction)
* **`fact_revenues`** (Fact) ➡️ joined to **`dim_customer_types`** on `cust_type_id` (1-to-many, Single cross-filtering direction)
* **`fact_revenues`** (Fact) ➡️ joined to **`dim_date`** on `date_key` (1-to-many, Single cross-filtering direction)
* **`fact_costs`** (Fact) ➡️ joined to **`dim_services`** on `service_id` (1-to-many, Single cross-filtering direction)

---

## 📊 Core DAX Calculations Library

### 1. Cumulative Revenue
```dax
[Profitability Cumulative Revenue] = 
SUM(fact_revenues[revenue_amount])
```

### 2. Cumulative Operational Overhead
```dax
[Profitability Cumulative Costs] = 
SUM(fact_costs[labor_costs]) + SUM(fact_costs[operational_costs]) + SUM(fact_costs[fixed_overhead])
```

### 3. Net Margin
```dax
[Profitability Net Profit] = 
[Profitability Cumulative Revenue] - [Profitability Cumulative Costs]
```

### 4. Profit Margin Percentage
```dax
[Profitability Net Margin %] = 
DIVIDE([Profitability Net Profit], [Profitability Cumulative Revenue], 0) * 100
```

---

## 📌 Dashboard Layout Wireframe Guide

### Page 1: Corporate Profitability Executive Overview
* **KPI Header Cards**:
  * Card 1: Total Service Revenue (Electric Blue glow)
  * Card 2: Cumulative Overhead Costs (Charcoal theme)
  * Card 3: Net Corporate Profits (Emerald Green glow)
  * Card 4: Profit Margin % (Teal conditional formatting)
* **Row 1 Chart**: Dual-axis Column & Line Chart mapping `[Profitability Cumulative Revenue]` vs `[Profitability Net Margin %]` by month index.
* **Row 2 Chart**: Clustered Bar Visual comparing Gross Net Profit by Service Line (`dim_services[service_line]`).
* **Row 3 Matrix Grid**: Multi-dimensional segmentation table matching region vs customer type with emerald data bars.
