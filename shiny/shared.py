from pathlib import Path

import pandas as pd
import duckdb

app_dir = Path(__file__).parent
df = pd.read_csv(app_dir / "penguins.csv")

app_root = Path(__file__).parent.parent

# Expenses data
persistence_db = duckdb.connect(database=str(app_root / "persist.duckdb"))
expenses_df = persistence_db.sql("select * from expenses;").df()
categories_df = persistence_db.sql("select * from transactions_cat;").df()

merged_df = pd.merge(expenses_df, categories_df, how="left", on="transaction", indicator=True)
merged_df = merged_df[["date", "card", "transaction", "amount", "category"]]
merged_df["amount"] = merged_df["amount"].apply(lambda x: round(x, 2))
# merged_df['date'] = pd.to_datetime(merged_df['date'], format='%Y-%m-%d')

aggregated_df = merged_df.groupby('category', as_index=False)['amount'].sum()

