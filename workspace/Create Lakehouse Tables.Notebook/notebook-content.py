# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "00000000-0000-0000-0000-000000000001",
# META       "default_lakehouse_name": "DemoDataLake",
# META       "default_lakehouse_workspace_id": "00000000-0000-0000-0000-000000000002",
# META       "known_lakehouses": [
# META         {
# META           "id": "00000000-0000-0000-0000-000000000001"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# Demo Notebook to load data

# CELL ********************

# ── Configuration ─────────────────────────────────────────────────────────────
# Files are loaded from the Lakehouse Files section — no external auth required.
# The Lakehouse name is parameterized by fabric-cicd during promotion.
print("Reading from Lakehouse Files/ ✓")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# ── Load CSV files from Lakehouse Files into delta tables ─────────────────────
tables = ["customers", "products", "sales_orders", "sales_territories"]

for table_name in tables:
    print(f"Loading {table_name}...")
    df = spark.read.option("header", True).option("inferSchema", True).csv(f"Files/{table_name}.csv")
    df.write.format("delta").mode("overwrite").saveAsTable(table_name)
    print(f"  ✓ {table_name}: {df.count()} rows")

print("\nAll tables loaded successfully!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#Demo1 Change

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
