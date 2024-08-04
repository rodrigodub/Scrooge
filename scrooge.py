#########################################################################################
# Scrooge
# Automation of Mastercard statement .data extraction and classification
# Author: Rodrigo Nobrega
# 20150407-20240804
#
# Usage:
# $ python3 scrooge.py
#########################################################################################
__version__ = 1.507

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
    Documentation
    """

    def __init__(self, bank_statement_file):
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
        pdf_file_object = open(self.filename, 'rb')
        print(f'  Opened file [{self.filename}]')
        # pdf_reader = PyPDF2.PdfFileReader(pdf_file_object)
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
        # np = self.pdfreader.numPages
        np = len(self.pdfreader.pages)
        print(f'\n Identifying number of pages in Bank Statement')
        return np

    def get_contents_page(self, num):
        pgobj = self.pdfreader.pages[num]
        pg = pgobj.extract_text()
        print(f' Retrieved contents of page {num}')
        return pg

    def return_date(self, string):
        try:
            # Attempt to parse the first part of the string as a date
            date = datetime.strptime(string.split(" ")[0], '%d/%m/%y')
            return date
        except ValueError:
            return None

    def read_expenses(self):
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
        """"""
        # Load the .env file
        load_dotenv(env_file)
        # Retrieve the variable value
        return os.getenv(variable_name)

    def convert_amount_to_float(self, amount):
        try:
            amount_float = float(amount.replace("$", "").replace(",", ""))
        except:
            amount_float = 0
        return amount_float

    def savecsv(self):
        pass


# Persist statement class
class Persistence(object):
    """
    Class to store statement results in a database, assign expenses
    into known categories and classify unknown categories
    """

    def __init__(self):
        self.con = duckdb.connect(database='persist.duckdb', read_only=False)
        self.categories = None
        self.expenses = None
        self.payments = None
        self.configure_persistence()

    def read_table(self, table_name):
        # Execute a query to fetch the table contents into a DataFrame
        df = self.con.execute(f"SELECT * FROM {table_name}").df()
        # Close the connection and return dataframe
        # self.con.close()
        return df

    def configure_persistence(self):
        print("\nPERSISTENCE:\n Configuring data persistence")
        self.categories = self.read_table("categories")
        self.expenses = self.read_table("expenses")
        self.payments = self.read_table("payments")

        self.expenses["amount"] = self.expenses["amount"].apply(lambda x: round(x, 2))
        self.payments["amount"] = self.payments["amount"].apply(lambda x: round(x, 2))

        return

    def add_transactions(self, transactions: CreditCard):
        # get the next IDs
        next_expenses_id = self.expenses["id"].idxmax() + 1
        next_payments_id = self.payments["id"].idxmax() + 1

        # find the new entries: Expenses
        new_expenses = pd.merge(transactions.expenses, self.expenses, how="left",
                                on=["date", "card", "transaction", "amount"],
                                indicator=True)
        new_expenses = new_expenses[new_expenses["_merge"] == "left_only"][["date", "card", "transaction", "amount"]]
        new_expenses = new_expenses.sort_values("date")
        new_expenses = new_expenses.reset_index(drop=True)
        new_expenses["id"] = new_expenses.index + next_expenses_id
        # Payments
        new_payments = pd.merge(transactions.payments, self.payments, how="left",
                                on=["date", "transaction", "amount"],
                                indicator=True)
        new_payments = new_payments[new_payments["_merge"] == "left_only"][["date", "transaction", "amount"]]
        new_payments = new_payments.sort_values("date")
        new_payments = new_payments.reset_index(drop=True)
        new_payments["id"] = new_payments.index + next_payments_id

        # Insert them if exist
        if len(new_expenses) > 0:
            print(" Inserting new expenses")
            self.con.sql("insert into expenses by name select * from new_expenses")
        else:
            print(" No expenses to insert")

        if len(new_payments) > 0:
            print(" Inserting new payments")
            self.con.sql("insert into payments by name select * from new_payments")
        else:
            print(" No payments to insert")

        return

    def get_new_transactions(self):
        pass

    def uncategorised_entries(self):
        pass

    def assign(self):
        pass

    def classify(self):
        pass

    def store(self):
        pass


# Visualise historic .data
class Visualise(object):
    """
    Matplotlib?
    """

    def __init__(self):
        pass


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
