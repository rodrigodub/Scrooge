#########################################################################################
# Scrooge
# Automation of Mastercard statement .data extraction and classification
# Author: Rodrigo Nobrega
# 20150407-20240727
#
# Usage:
# $ python3 scrooge.py
#########################################################################################
__version__ = 1.505


# import libraries
import os
from datetime import datetime
from dotenv import load_dotenv
import PyPDF2
import pandas as pd


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
        print(f'Creating credit card statement')
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
        print(f'Opened file [{self.filename}]')
        # pdf_reader = PyPDF2.PdfFileReader(pdf_file_object)
        pdf_reader = PyPDF2.PdfReader(pdf_file_object)
        print(f'Read [{self.filename}] PDF contents')
        # Check if the PDF is encrypted
        if pdf_reader.is_encrypted:
            try:
                # Try to decrypt the PDF with the provided password
                pdf_reader.decrypt(self.get_env_variable(".env", "CC"))
            except Exception as e:
                print(f"Failed to decrypt PDF: {e}")
                return None
        return pdf_reader

    def get_number_of_pages(self):
        # np = self.pdfreader.numPages
        np = len(self.pdfreader.pages)
        print(f'Identifying number of pages')
        return np

    def get_contents_page(self, num):
        pgobj = self.pdfreader.pages[num]
        pg = pgobj.extract_text()
        print(f'Retrieved contents of page {num}')
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
                                   columns=["Date", "Card", "Transaction", "Amount"])
        payments_df = pd.DataFrame([[i.split(" ")[0],
                                     " ".join(i.split(" ")[1:-1]),
                                     i.split(" ")[-1]] for i in payments_list],
                                   columns=["Date", "Transaction", "Amount"])
        # output dataframes
        return expenses_df, payments_df

    def get_env_variable(self, env_file, variable_name):
        """"""
        # Load the .env file
        load_dotenv(env_file)
        # Retrieve the variable value
        return os.getenv(variable_name)

    def savecsv(self):
        pass


# Persist statement class
class Persist(object):
    """
    Class to store statement results in a database, assign expenses
    into known categories and classify unknown categories
    """
    def __init__(self):
        self.db = None

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
    statement = ".data/2406 Email Statement.pdf"
    # pdf_file_object = open(statement, 'rb')
    #
    # pdf_reader = PyPDF2.PdfReader(pdf_file_object)
    # print(f"pdf_reader.is_encrypted: {pdf_reader.is_encrypted}")
    #
    # pwd = Cc(statement).get_env_variable(".env", "CC")
    # print(f"Password: {pwd}\n")

    # Create Credit Card instance
    # cc1 = Cc(FILE_PATH)
    cc1 = CreditCard(statement)

    print(f"Number of pages: {cc1.num_pages}")
    # print contents
    # [print(i) for i in cc1.rawexpenses]
    print('\n---------------------------------------\n')
    # [print(i) for i in cc1.processed]
    print('\n=========================== END OF PROGRAM ==============================--\n')

    return cc1


# main, calling main loop
if __name__ == '__main__':
    main()


