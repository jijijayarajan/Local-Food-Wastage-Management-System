"""
load_data.py
-------------
Cleans the four source CSVs and loads them into the MySQL
`food_waste_db` database created by sql/schema.sql.

Run schema.sql FIRST (creates the empty tables), then run this script.

Usage:
    python load_data.py
"""

import pandas as pd
from sqlalchemy import create_engine

# ------------------------------------------------------------------
# 1. EDIT THESE to match your local MySQL setup
# ------------------------------------------------------------------
DB_USER = "root"
DB_PASSWORD = "Aieden@1993"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "food_wastage"
DATA_DIR = "."

# ------------------------------------------------------------------
# 2. Load raw CSVs
# ------------------------------------------------------------------
providers = pd.read_csv(f"{DATA_DIR}/providers_data.csv")
receivers = pd.read_csv(f"{DATA_DIR}/receivers_data.csv")
food = pd.read_csv(f"{DATA_DIR}/food_listings_data.csv")
claims = pd.read_csv(f"{DATA_DIR}/claims_data.csv")

# ------------------------------------------------------------------
# 3. Clean / standardize
# ------------------------------------------------------------------

# --- Food listings: parse Expiry_Date (format is M/D/YYYY) ---
food["Expiry_Date"] = pd.to_datetime(food["Expiry_Date"], format="%m/%d/%Y")

# Strip whitespace on key text columns across all tables
for df in (providers, receivers, food, claims):
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

# --- Claims: Timestamp has TWO mixed formats in the source data:
#     "03-05-2025"        -> MM-DD-YYYY  (date only)
#     "3/21/2025 0:59"     -> M/D/YYYY H:MM (date + time)
# pandas' mixed format inference handles both in one pass.
claims["Timestamp"] = pd.to_datetime(claims["Timestamp"], format="mixed")

# --- Drop exact duplicate rows, if any ---
providers = providers.drop_duplicates(subset="Provider_ID")
receivers = receivers.drop_duplicates(subset="Receiver_ID")
food = food.drop_duplicates(subset="Food_ID")
claims = claims.drop_duplicates(subset="Claim_ID")

# --- Sanity check referential integrity before loading ---
orphan_food = ~food["Provider_ID"].isin(providers["Provider_ID"])
orphan_claims_food = ~claims["Food_ID"].isin(food["Food_ID"])
orphan_claims_recv = ~claims["Receiver_ID"].isin(receivers["Receiver_ID"])

assert orphan_food.sum() == 0, f"{orphan_food.sum()} food rows reference unknown Provider_ID"
assert orphan_claims_food.sum() == 0, f"{orphan_claims_food.sum()} claims reference unknown Food_ID"
assert orphan_claims_recv.sum() == 0, f"{orphan_claims_recv.sum()} claims reference unknown Receiver_ID"

print("Data cleaned. Row counts:")
print(f"  providers      : {len(providers)}")
print(f"  receivers      : {len(receivers)}")
print(f"  food_listings  : {len(food)}")
print(f"  claims         : {len(claims)}")

# ------------------------------------------------------------------
# 4. Load into MySQL
#    NOTE: schema.sql must have been run already (tables must exist)
#    so that foreign keys are enforced. We load in dependency order:
#    providers -> receivers -> food_listings -> claims
# ------------------------------------------------------------------
engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD.replace('@','%40')}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

providers.to_sql("providers", engine, if_exists="append", index=False)
receivers.to_sql("receivers", engine, if_exists="append", index=False)
food.to_sql("food_listings", engine, if_exists="append", index=False)
claims.to_sql("claims", engine, if_exists="append", index=False)
print("\nAll tables loaded into MySQL successfully.")


