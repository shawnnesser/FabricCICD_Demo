"""
post_deploy.py - Post-deployment tasks for a Fabric workspace.

After fabric-cicd deploys item definitions, this script:
  1. Generates environment-specific synthetic data (no git/ADLS dependency)
  2. Uploads CSV data files into the target Lakehouse Files section via OneLake
  3. Triggers the "Create Lakehouse Tables" notebook to load delta tables
  4. Waits for the notebook run to complete

Data volumes and characteristics differ per environment to demonstrate
a real CI/CD pipeline with environment-specific test data:

  dev  - 50 rows,  recent quarter, East region  (developer sandbox)
  test - 200 rows, full year,      West region  (QA validation)
  prod - SKIP automatic data load; prod data is managed by data engineers

Usage:
    python src/post_deploy.py --environment test
    python src/post_deploy.py --environment prod

Environment variables required in CI:
    AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET

Local runs can also load the same values from Azure Key Vault or Azure CLI.
"""

import argparse
import csv
import io
import os
import random
import sys
import time

import requests
from auth_helper import get_token_credential

LAKEHOUSE_NAME = "DemoDataLake"
NOTEBOOK_NAME  = "Create Lakehouse Tables"

# ── Environment-specific data profiles ────────────────────────────────────────
DATA_PROFILES = {
    "dev": {
        "description": "Developer sandbox — 50 rows, Q4 2026, East region",
        "num_customers":  20,
        "num_products":   10,
        "num_orders":     50,
        "year":           2026,
        "quarter_start":  10,   # October–December
        "regions":        ["East"],
    },
    "test": {
        "description": "QA validation — 200 rows, full year 2025, West region",
        "num_customers":  60,
        "num_products":   25,
        "num_orders":     200,
        "year":           2025,
        "quarter_start":  1,    # January–December
        "regions":        ["West", "Northwest"],
    },
}


# ── Synthetic data generators ──────────────────────────────────────────────────

def make_customers(n, regions):
    rows = [["CustomerID","FirstName","LastName","CompanyName","EmailAddress","City","StateProvince","CountryRegion","PostalCode"]]
    first_names = ["Alice","Bob","Carol","David","Eva","Frank","Grace","Henry","Iris","Jack","Karen","Leo","Mary","Nathan","Olivia"]
    last_names  = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Wilson","Moore"]
    companies   = ["Alpine Bikes","Scenic Tours","Pacific Cycles","Summit Sports","Valley Fitness"]
    cities_by_region = {
        "East":      [("Boston","Massachusetts"),("New York","New York"),("Philadelphia","Pennsylvania")],
        "West":      [("Los Angeles","California"),("Seattle","Washington"),("Phoenix","Arizona")],
        "Northwest": [("Portland","Oregon"),("Bellevue","Washington"),("Spokane","Washington")],
    }
    for i in range(1, n + 1):
        region = random.choice(regions)
        city, state = random.choice(cities_by_region.get(region, [("Chicago","Illinois")]))
        fn, ln = random.choice(first_names), random.choice(last_names)
        rows.append([i, fn, ln, random.choice(companies), f"{fn.lower()}{i}@example.com",
                     city, state, "United States", f"{random.randint(10000,99999)}"])
    return rows

def make_products(n):
    rows = [["ProductID","Name","ProductNumber","Color","StandardCost","ListPrice","Size","Weight","Category"]]
    names = ["Mountain Bike","Road Bike","Touring Bike","Sport Helmet","Classic Helmet",
             "Water Bottle","Bike Stand","Fender Set","Gloves","Shorts","Jersey","Socks",
             "Chain","Tire","Pedals","Saddle","Handlebar","Pump","Lock","Bag"]
    colors = ["Black","Silver","Red","Blue","Yellow","White"]
    cats   = ["Bikes","Accessories","Clothing","Components"]
    for i in range(1, n + 1):
        cost  = round(random.uniform(5, 500), 2)
        price = round(cost * random.uniform(1.2, 2.5), 2)
        rows.append([i, random.choice(names[:n]), f"PR-{i:04d}", random.choice(colors),
                     cost, price, random.choice(["S","M","L","XL",""]),
                     round(random.uniform(0.1, 15), 2), random.choice(cats)])
    return rows

def make_sales_orders(n, num_customers, num_products, year, quarter_start):
    rows = [["SalesOrderID","OrderDate","DueDate","ShipDate","CustomerID","ProductID","OrderQty","UnitPrice","LineTotal"]]
    month_range = range(quarter_start, min(quarter_start + 12, 13))
    for i in range(1, n + 1):
        month = random.choice(list(month_range))
        day   = random.randint(1, 28)
        date  = f"{year}-{month:02d}-{day:02d}"
        due   = f"{year}-{month:02d}-{min(day+7,28):02d}"
        ship  = f"{year}-{month:02d}-{min(day+3,28):02d}"
        cid   = random.randint(1, num_customers)
        pid   = random.randint(1, num_products)
        qty   = random.randint(1, 10)
        price = round(random.uniform(10, 500), 2)
        rows.append([i, date, due, ship, cid, pid, qty, price, round(qty * price, 2)])
    return rows

def make_territories(regions):
    rows = [["TerritoryID","Name","CountryRegionCode","Group"]]
    for i, region in enumerate(["Northeast","Northwest","Southeast","Southwest","Central","Canada","France","Germany","Australia","United Kingdom"], 1):
        rows.append([i, region, "US" if i <= 6 else ["CA","FR","DE","AU","GB"][i-7], "North America" if i<=6 else "International"])
    return rows


def csv_bytes(rows):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


# ── Fabric / OneLake helpers ───────────────────────────────────────────────────

def get_fabric_token(credential):
    return credential.get_token("https://api.fabric.microsoft.com/.default").token

def get_storage_token(credential):
    return credential.get_token("https://storage.azure.com/.default").token

def find_item(token, workspace_id, item_type, name):
    r = requests.get(
        f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    for item in r.json().get("value", []):
        if item.get("type") == item_type and item.get("displayName") == name:
            return item["id"]
    return None

def upload_to_lakehouse(storage_token, workspace_id, lakehouse_id, filename, content):
    base = f"https://onelake.dfs.fabric.microsoft.com/{workspace_id}/{lakehouse_id}/Files"
    h    = {"Authorization": f"Bearer {storage_token}", "x-ms-version": "2023-11-03"}
    requests.put(f"{base}/{filename}?resource=file", headers=h, timeout=30).raise_for_status()
    requests.patch(f"{base}/{filename}?action=append&position=0",
                   headers={**h, "Content-Type": "application/octet-stream"},
                   data=content, timeout=60).raise_for_status()
    requests.patch(f"{base}/{filename}?action=flush&position={len(content)}",
                   headers=h, timeout=30).raise_for_status()

def run_notebook(fabric_token, workspace_id, notebook_id):
    r = requests.post(
        f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items/{notebook_id}/jobs/instances?jobType=RunNotebook",
        headers={"Authorization": f"Bearer {fabric_token}"},
        json={}, timeout=30,
    )
    r.raise_for_status()
    location = r.headers.get("Location", "")
    return location.rstrip("/").split("/")[-1] if location else None

def wait_for_job(fabric_token, workspace_id, notebook_id, job_id):
    print(f"[INFO] Waiting for notebook job {job_id}...")
    for _ in range(60):
        time.sleep(30)
        r = requests.get(
            f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items/{notebook_id}/jobs/instances/{job_id}",
            headers={"Authorization": f"Bearer {fabric_token}"},
            timeout=30,
        )
        if r.status_code == 200:
            status = r.json().get("status", "Unknown")
            print(f"[INFO]   Status: {status}")
            if status in ("Completed", "Succeeded"):
                return
            if status in ("Failed", "Cancelled", "Deduped"):
                print(f"[ERROR] Notebook job ended with status: {status}", file=sys.stderr)
                sys.exit(1)
    print("[ERROR] Notebook job timed out", file=sys.stderr)
    sys.exit(1)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", required=True, choices=["test", "prod"])
    args = parser.parse_args()
    env = args.environment

    if env == "prod":
        print("[INFO] prod environment: skipping automatic data load.")
        print("[INFO] Prod data is managed by data engineers and loaded separately.")
        return

    profile = DATA_PROFILES[env]
    workspace_id_variable = f"FABRIC_{env.upper()}_WORKSPACE_ID"
    workspace_id = os.environ.get(workspace_id_variable)
    if not workspace_id:
        parser.error(f"{workspace_id_variable} must be set for post-deployment tasks.")

    print(f"[INFO] Post-deploy: {env} — {profile['description']}")
    print(f"[INFO] Workspace: {workspace_id}")

    random.seed(42 if env == "dev" else 99)   # Reproducible per environment

    try:
        credential = get_token_credential(env)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    fabric_token  = get_fabric_token(credential)
    storage_token = get_storage_token(credential)

    print(f"[INFO] Looking for Lakehouse '{LAKEHOUSE_NAME}'...")
    lakehouse_id = find_item(fabric_token, workspace_id, "Lakehouse", LAKEHOUSE_NAME)
    if not lakehouse_id:
        print(f"[ERROR] Lakehouse not found in workspace", file=sys.stderr)
        sys.exit(1)
    print(f"[INFO] Found Lakehouse: {lakehouse_id}")

    # Generate and upload environment-specific data
    datasets = {
        "customers.csv":        csv_bytes(make_customers(profile["num_customers"], profile["regions"])),
        "products.csv":         csv_bytes(make_products(profile["num_products"])),
        "sales_orders.csv":     csv_bytes(make_sales_orders(
                                    profile["num_orders"], profile["num_customers"],
                                    profile["num_products"], profile["year"], profile["quarter_start"])),
        "sales_territories.csv": csv_bytes(make_territories(profile["regions"])),
    }

    for filename, content in datasets.items():
        print(f"[INFO] Uploading {filename} ({len(content)} bytes)...")
        upload_to_lakehouse(storage_token, workspace_id, lakehouse_id, filename, content)
        print(f"[INFO]   uploaded")

    print(f"[INFO] Looking for Notebook '{NOTEBOOK_NAME}'...")
    notebook_id = find_item(fabric_token, workspace_id, "Notebook", NOTEBOOK_NAME)
    if not notebook_id:
        print(f"[WARN] Notebook not found — skipping data load.")
        return

    print(f"[INFO] Triggering notebook run...")
    job_id = run_notebook(fabric_token, workspace_id, notebook_id)
    if job_id:
        wait_for_job(fabric_token, workspace_id, notebook_id, job_id)
        print("[INFO] Notebook completed — delta tables populated")
    else:
        print("[WARN] Could not get job ID — check manually.")

    print(f"[INFO] Post-deploy complete for '{env}'.")


if __name__ == "__main__":
    main()
