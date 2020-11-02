#########################################################################################
# Scrooge
# Automation of Mastercard statement data extraction and classification
# Author: Rodrigo Nobrega
# 20150407-20201102
#
# Usage:
# $ python3 scrooge.py
#########################################################################################
__version__ = 1.113


# import libraries
import PyPDF2
import pandas as pd


# global variables
FILE_PATH = '20201026a.pdf'


# read PDF
# pdfFileObj = open(FILE_PATH, 'rb')
# pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
# find and print number of pages
# np = pdfReader.numPages
# print(f'Number of pages: {np}')
# get the contents of page 1
# pageObj = pdfReader.getPage(2)
# a = pageObj.extractText()
# print(a)


# CreditCard statement Class
class Cc(object):
    """
    Documentation
    """
    def __init__(self, statementfile):
        print(f'Creating credit card statement')
        self.filename = statementfile
        self.pdfreader = self.readstatement()
        self.numpages = self.getnumberofpages()
        self.expenses = self.getcontentspage(2)

    def readstatement(self):
        pdfFileObj = open(self.filename, 'rb')
        print(f'Opened file [{self.filename}]')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        print(f'Read [{self.filename}] PDF contents')
        return pdfReader

    def getnumberofpages(self):
        np = self.pdfreader.numPages
        print(f'Identifying number of pages')
        return np

    def getcontentspage(self, num):
        pgobj = self.pdfreader.getPage(num)
        print(f'Retrieving contents of page {num}')
        pg = pgobj.extractText()
        print(f'Done')
        return pg

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


# Visualise historic data
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
    # Create Credit Card instance
    cc1 = Cc(FILE_PATH)
    # print contents
    print(cc1.expenses)
    print('\n=========================== END OF PROGRAM ==============================--\n')


# main, calling main loop
if __name__ == '__main__':
    main()


