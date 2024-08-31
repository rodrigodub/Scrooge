#########################################################################################
# Scrooge
# Automation of Mastercard statement .data extraction and classification
# Author: Rodrigo Nobrega
# 20150407-20240831
#
# Usage:
# $ python3 scrooge.py
#########################################################################################
__version__ = 1.511

# import libraries
import os
from datetime import datetime
from dotenv import load_dotenv
import PyPDF2
import pandas as pd
import duckdb

# global variables
ENVIRONMENT = ".env"
FILE_PATH = '20190226a.pdf'
# FILE_PATH = '20201026a.pdf'
EXCEPTIONS = ['OPENING BALANCE', 'HSBC BANK PAYMENT', 'CLOSING BALANCE', 'ORIGINAL TRANSACTION AMOUNT',
              'OVERSEAS TRANSACTION FEE']


# CreditCard statement Class
class CreditCard(object):
    """
    A class to represent a Credit Card statement.

    Attributes
    ----------
    filename : str
        The path to the bank statement PDF file.
    pdfreader : PyPDF2.PdfReader
        The PDF reader object to read the PDF file.
    num_pages : int
        The number of pages in the PDF file.
    raw_expenses : list
        A list of raw contents from each page of the PDF.
    expenses : pd.DataFrame
        A DataFrame containing processed expenses.
    payments : pd.DataFrame
        A DataFrame containing processed payments.
    """

    def __init__(self, bank_statement_file):
        """
        Constructs all the necessary attributes for the CreditCard object.

        Parameters
        ----------
        bank_statement_file : str
            The path to the bank statement PDF file.
        """
        print('\nCREDIT CARD:\n Creating credit card statement')
        # read the file contents
        self.filename = bank_statement_file
        self.pdfreader = self.read_bank_statement()
        # define number of pages
        self.num_pages = self.get_number_of_pages()
        # iterate through pages and create a list with their raw contents
        self.raw_expenses = [self.get_contents_page(i) for i in range(self.num_pages)]
        # process expenses
        self.expenses, self.payments = self.read_expenses()

    def read_bank_statement(self):
        """
        Reads the bank statement PDF file.

        Returns
        -------
        PyPDF2.PdfReader
            The PDF reader object to read the PDF file.
        """
        pdf_file_object = open(self.filename, 'rb')
        print(f'  Opened file [{self.filename}]')
        pdf_reader = PyPDF2.PdfReader(pdf_file_object)
        print(f'  Read [{self.filename}] PDF contents')

        # Check if the PDF is encrypted
        if pdf_reader.is_encrypted:
            try:
                # Try to decrypt the PDF with the provided password
                pdf_reader.decrypt(self.get_env_variable(".env", "CC"))
            except Exception as e:
                print(f"  Failed to decrypt PDF: {e}")
                return None
        return pdf_reader

    def get_number_of_pages(self):
        """
        Gets the number of pages in the PDF file.

        Returns
        -------
        int
            The number of pages in the PDF file.
        """
        np = len(self.pdfreader.pages)
        print(f'\n Identifying number of pages in Bank Statement')
        return np

    def get_contents_page(self, num):
        """
        Gets the contents of a specific page in the PDF file.

        Parameters
        ----------
        num : int
            The page number to extract contents from.

        Returns
        -------
        str
            The text contents of the specified page.
        """
        pgobj = self.pdfreader.pages[num]
        pg = pgobj.extract_text()
        print(f' Retrieved contents of page {num}')
        return pg

    def return_date(self, string):
        """
        Attempts to parse a date from a string.

        Parameters
        ----------
        string : str
            The string to parse the date from.

        Returns
        -------
        datetime or None
            The parsed date if successful, otherwise None.
        """
        try:
            # Attempt to parse the first part of the string as a date
            date = datetime.strptime(string.split(" ")[0], '%d/%m/%y')
            return date
        except ValueError:
            return None

    def read_expenses(self):
        """
        Processes the raw expenses and payments from the PDF.

        Returns
        -------
        tuple
            A tuple containing two DataFrames: expenses and payments.
        """
        transactions_only = []
        # concatenate all pages from the PDF
        all_lines = "\n".join(self.raw_expenses)
        # one entry per line
        all_lines = all_lines.split("\n")
        # select only lines that start with a date
        for line in all_lines:
            if self.return_date(line):
                transactions_only.append(line)

        # Filtering the strings list
        expenses_list = [
            string for string in transactions_only
            if not any(string_part in string for string_part in EXCEPTIONS)
        ]
        payments_list = [
            string for string in transactions_only
            if any(string_part in string for string_part in EXCEPTIONS)
        ]

        # create dataframes
        expenses_df = pd.DataFrame([[i.split(" ")[0],
                                     i.split(" ")[1],
                                     " ".join(i.split(" ")[2:-1]),
                                     i.split(" ")[-1]] for i in expenses_list],
                                   columns=["date", "card", "transaction", "amount"])
        payments_df = pd.DataFrame([[i.split(" ")[0],
                                     " ".join(i.split(" ")[1:-1]),
                                     i.split(" ")[-1]] for i in payments_list],
                                   columns=["date", "transaction", "amount"])

        # convert amount to float
        expenses_df["amount"] = expenses_df["amount"].apply(lambda x: self.convert_amount_to_float(x))
        payments_df["amount"] = payments_df["amount"].apply(lambda x: self.convert_amount_to_float(x))

        # convert date to datetime
        expenses_df["date"] = expenses_df["date"].apply(lambda x: self.return_date(x))
        payments_df["date"] = payments_df["date"].apply(lambda x: self.return_date(x))

        # output dataframes
        return expenses_df, payments_df

    def get_env_variable(self, env_file, variable_name):
        """
        Retrieves the value of a variable from a .env file.

        Parameters
        ----------
        env_file : str
            The path to the .env file.
        variable_name : str
            The name of the variable to retrieve.

        Returns
        -------
        str
            The value of the specified variable.
        """
        # Load the .env file
        load_dotenv(env_file)
        # Retrieve the variable value
        return os.getenv(variable_name)

    def convert_amount_to_float(self, amount):
        """
        Converts an amount string to a float.

        Parameters
        ----------
        amount : str
            The amount string to convert.

        Returns
        -------
        float
            The converted float value of the amount.
        """
        try:
            amount_float = float(amount.replace("$", "").replace(",", ""))
        except:
            amount_float = 0
        return amount_float


# Persist statement class
class Persistence(object):
    """
    A class to store statement results in a database, assign expenses
    into known categories, and classify unknown categories.

    Attributes
    ----------
    con : duckdb.DuckDBPyConnection
        The DuckDB database connection.
    categories : pd.DataFrame
        DataFrame containing the categories table.
    expenses : pd.DataFrame
        DataFrame containing the expenses table.
    payments : pd.DataFrame
        DataFrame containing the payments table.
    transaction_categories : pd.DataFrame
        DataFrame containing the transaction categories table.
    """

    def __init__(self):
        """
        Initializes the Persistence class by setting up the database connection
        and configuring data persistence.
        """
        self.con = duckdb.connect(database='persist.duckdb', read_only=False)
        self.categories = None
        self.expenses = None
        self.payments = None
        self.transaction_categories = None
        self.configure_persistence()

    def read_table(self, table_name):
        """
        Reads the contents of a table from the database into a DataFrame.

        Parameters
        ----------
        table_name : str
            The name of the table to read.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the table contents.
        """
        # Execute a query to fetch the table contents into a DataFrame
        df = self.con.execute(f"SELECT * FROM {table_name}").df()
        return df

    def configure_persistence(self):
        """
        Configures data persistence by reading the necessary tables from the database
        and performing any necessary setup.
        """
        print("\nPERSISTENCE:\n Configuring data persistence")
        self.categories = self.read_table("categories")
        self.expenses = self.read_table("expenses")
        self.payments = self.read_table("payments")
        self.transaction_categories = self.read_table("transactions_cat")

        # Round the amounts to 2 decimal places
        self.expenses["amount"] = self.expenses["amount"].apply(lambda x: round(x, 2))
        self.payments["amount"] = self.payments["amount"].apply(lambda x: round(x, 2))

    def add_transactions(self, transactions: CreditCard):
        """
        Adds new transactions from a CreditCard object to the database.

        Parameters
        ----------
        transactions : CreditCard
            The CreditCard object containing the new transactions.
        """
        # Get the next IDs
        next_expenses_id = self.expenses["id"].max() + 1
        next_payments_id = self.payments["id"].max() + 1

        # Find the new entries: Expenses
        new_expenses = pd.merge(transactions.expenses, self.expenses, how="left",
                                on=["date", "card", "transaction", "amount"],
                                indicator=True)
        new_expenses = new_expenses[new_expenses["_merge"] == "left_only"][["date", "card", "transaction", "amount"]]
        new_expenses = new_expenses.sort_values("date").reset_index(drop=True)
        new_expenses["id"] = new_expenses.index + next_expenses_id

        # Find the new entries: Payments
        new_payments = pd.merge(transactions.payments, self.payments, how="left",
                                on=["date", "transaction", "amount"],
                                indicator=True)
        new_payments = new_payments[new_payments["_merge"] == "left_only"][["date", "transaction", "amount"]]
        new_payments = new_payments.sort_values("date").reset_index(drop=True)
        new_payments["id"] = new_payments.index + next_payments_id

        # Insert new expenses if they exist
        if len(new_expenses) > 0:
            print(" Inserting new expenses")
            self.con.sql("insert into expenses by name select * from new_expenses")
        else:
            print(" No expenses to insert")

        # Insert new payments if they exist
        if len(new_payments) > 0:
            print(" Inserting new payments")
            self.con.sql("insert into payments by name select * from new_payments")
        else:
            print(" No payments to insert")

    def get_unclassified_transactions(self):
        """
        Retrieves transactions that have not been classified and saves them to a CSV file.

        Returns
        -------
        pd.DataFrame
            DataFrame containing unclassified transactions.
        """
        unclassified = self.con.sql(
            "SELECT DISTINCT transaction, NULL as category FROM expenses "
            "WHERE transaction NOT IN (SELECT transaction FROM transactions_cat)"
        ).df()
        filename = f".data/unclassified_transactions_{datetime.now().strftime('%y%m%d%H%M')}.csv"
        unclassified.to_csv(filename, index=False)
        return unclassified

    def upload_classified_transactions(self, csv_file):
        """
        Uploads classified transactions from a CSV file to the database.

        Parameters
        ----------
        csv_file : str
            The path to the CSV file containing classified transactions.
        """
        new_classifications = pd.read_csv(csv_file)
        new_classifications = new_classifications[~new_classifications["category"].isna()].reset_index(drop=True)
        next_classifications_id = self.transaction_categories["id"].max() + 1
        new_classifications["id"] = new_classifications.index + next_classifications_id

        try:
            self.con.sql(
                "insert into transactions_cat by name select * from new_classifications;"
            )
            print(" OK")
        except Exception as e:
            print(f" Could not store new classifications: {e}")
            return None

        # Refresh data
        print(" Refreshing data")
        self.configure_persistence()
        return




# main loop
def main():
    print('\n===========================================================================')
    print('                                 Scrooge')
    print('===========================================================================\n')

    # Get the bank statement file
    # statement = ".data/2406 Email Statement.pdf"
    bank_statement = input(" Enter the Credit Card Bank Statement to import: \n  ")

    # Create Credit Card instance
    cc = CreditCard(bank_statement)

    # Create the Persistence instance
    persist = Persistence()

    # Add the new entries
    persist.add_transactions(cc)
    print('\n---------------------------------------\n')
    # [print(i) for i in cc1.processed]
    print('\n=========================== END OF PROGRAM ==============================--\n')

    return


# main, calling main loop
if __name__ == '__main__':
    main()
