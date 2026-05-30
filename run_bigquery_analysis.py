import os
import sys
import json
import pandas as pd
import pydata_google_auth

def main():
    print("👉 Starting Profitability BigQuery Cloud Ingestion Engine...")
    processed_dir = "data/processed"
    if not os.path.exists(processed_dir):
        print("Please execute main.py first.")
        sys.exit(1)

    tables = {
        "dim_services_profit": "dim_services.csv",
        "dim_regions_profit": "dim_regions.csv",
        "dim_customer_types_profit": "dim_customer_types.csv",
        "dim_date_profit": "dim_date.csv",
        "fact_revenues_profit": "fact_revenues.csv",
        "fact_costs_profit": "fact_costs.csv",
        "service_profit_report": "service_profit_report.csv",
        "mom_profit_trends": "mom_profit_trends.csv",
        "regional_customer_performance": "regional_customer_performance.csv"
    }

    project_id = os.environ.get("GCP_PROJECT_ID", "").strip()
    if not project_id:
        project_id = input("Enter GCP Project ID: ").strip()

    print("\n🔐 Authenticating with GCP...")
    try:
        credentials = None
        gcp_key = os.environ.get("GCP_CREDENTIALS")
        if gcp_key:
            import google.oauth2.service_account
            credentials = google.oauth2.service_account.Credentials.from_service_account_info(
                json.loads(gcp_key), scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
        elif os.path.exists("data/gcp_credentials.json"):
            import google.oauth2.service_account
            credentials = google.oauth2.service_account.Credentials.from_service_account_file(
                "data/gcp_credentials.json", scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
        else:
            credentials = pydata_google_auth.get_user_credentials(
                scopes=["https://www.googleapis.com/auth/cloud-platform"], auth_local_webserver=True
            )
            
        from google.cloud import bigquery
        client = bigquery.Client(project=project_id, credentials=credentials)
        dataset_id = f"{project_id}.apex_analytics"
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        try:
            client.get_dataset(dataset_id)
        except Exception:
            client.create_dataset(dataset, timeout=30)

        for table, csv_file in tables.items():
            csv_path = os.path.join(processed_dir, csv_file)
            df = pd.read_csv(csv_path)
            df.to_gbq(
                destination_table=f"apex_analytics.{table}",
                project_id=project_id,
                credentials=credentials,
                if_exists="replace"
            )
            print(f"✅ Loaded {len(df)} rows into 'apex_analytics.{table}'")
            
        print("\n🎉 SUCCESS! ALL PROFITABILITY SCHEMAS COMPLED IN GCP BIGQUERY!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
