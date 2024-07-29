import duckdb


# Initialize the DuckDB connection and create a table if it doesn't exist
def init_db():
    con = duckdb.connect(database='persist.duckdb', read_only=False)

    con.execute("""CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY,
                    date DATE,
                    card VARCHAR,
                    transaction VARCHAR,
                    amount FLOAT
                    )""")

    con.execute("""CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY,
                    date DATE,
                    transaction VARCHAR,
                    amount FLOAT
                    )""")

    con.execute("""CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY,
                    category VARCHAR
                    )""")

    con.execute("""CREATE TABLE IF NOT EXISTS transactions_cat (
                        id INTEGER PRIMARY KEY,
                        transaction VARCHAR,
                        category VARCHAR
                        )""")

    con.close()


# Initialize the database
init_db()
# duckdb.sql("INSERT INTO my_table SELECT * FROM my_df")