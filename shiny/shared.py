from pathlib import Path

import pandas as pd
import duckdb

app_dir = Path(__file__).parent
df = pd.read_csv(app_dir / "penguins.csv")

app_root = Path(__file__).parent.parent
persistence_db = duckdb.connect(database=str(app_root / "persist.duckdb"))
expenses_df = persistence_db.sql("select * from expenses;").df()
categories_df = persistence_db.sql("select * from transactions_cat;").df()
merged_df = pd.merge(expenses_df, categories_df, how="left", on="transaction", indicator=True)
aggregated_df = merged_df.groupby('category', as_index=False)['amount'].sum()
