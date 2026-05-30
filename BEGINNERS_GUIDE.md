# Beginner's Guide: B2B Corporate Service Profitability Analysis

This step-by-step guide explains how to install, execute, and verify this profitability pipeline from scratch with zero programming knowledge.

---

## 💻 1. Local Pipeline Setup

1. **Open PowerShell** on Windows.
2. **Clone the repository** and navigate to the project directory:
   ```powershell
   cd C:\Users\vaibh\Documents\antigravity\profitability-analysis
   ```
3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
4. **Execute the local orchestrator**:
   ```powershell
   python main.py
   ```
   This will:
   * Generate simulated invoicing spreadsheets and monthly cost sheets with casing and date noise.
   * Cleans dates, standardise titles, and maps them to a Star Schema.
   * Run the **20-point Data Quality Validation Suite** verifying database integrity.
   * Ingest and build a relational database at `data/profitability.db`.
   * Compile and export the analytical SQL CTE reports to `data/processed/`.

---

## 🧪 2. Run Quality Assurance Unit Tests

Run the following command to execute all automated test assertions:
```powershell
python -m pytest tests/ -v
```

---

## ☁️ 3. Google BigQuery Cloud Integration

1. Set up a dedicated Google Cloud Platform (GCP) project.
2. In your shell, set your target GCP Project ID environment variable:
   ```powershell
   $env:GCP_PROJECT_ID="your-project-id"
   ```
3. Run the uploader command:
   ```powershell
   python run_bigquery_analysis.py
   ```
   This will authenticate with your GCP credentials, stream all processed facts and dimensions to BigQuery under the dataset `apex_analytics`, and compile a permanent SQL Analytical View (`view_profitability_margins`) directly in the cloud.
