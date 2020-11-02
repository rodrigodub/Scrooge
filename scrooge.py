#########################################################################################
# Scrooge
# Automation of Mastercard statement data extraction and classification
# Author: Rodrigo Nobrega
# 20150407-20201102
#
# Usage:
# $ python3 scrooge.py
#########################################################################################
__version__ = 1.112


# import libraries
import PyPDF2
import pandas as pd


# global variables
FILE_PATH = '20201026a.pdf'


# # read PDF
# pdfFileObj = open(FILE_PATH, 'rb')
# pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
# # find and print number of pages
# np = pdfReader.numPages
# print(f'Number of pages: {np}')
# # get the contents of page 1
# pageObj = pdfReader.getPage(2)
# a = pageObj.extractText()
# print(a)


# CreditCard statement Class
class Cc(object):
    """
    Documentation
    """
    def __init__(self):
        self.file = None
        self.expenses = None

    def readstatement(self):
        pass

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

    print('\n=========================== END OF PROGRAM ==============================--\n')


# main, calling main loop
if __name__ == '__main__':
    main()


