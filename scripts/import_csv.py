# scripts/import_csv.py
import pandas as pd
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

df = pd.read_csv("data_nettoyee/data_simulate_2024.csv")
df.to_sql("tdengue2", engine, if_exists="append", index=False)