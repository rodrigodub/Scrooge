#########################################################################################
# Scrooge
# Automation of Mastercard statement data extraction and classification
# Author: Rodrigo Nobrega
# 20150407-20201105
#
# Usage:
# $ python3 scrooge.py
#########################################################################################
__version__ = 1.115


# import libraries
import PyPDF2
import pandas as pd


# global variables
FILE_PATH = '20190226a.pdf'
# FILE_PATH = '20201026a.pdf'


# CreditCard statement Class
class Cc(object):
    """
    Documentation
    """
    def __init__(self, statementfile):
        print(f'Creating credit card statement')
        # read the file contents
        self.filename = statementfile
        self.pdfreader = self.readstatement()
        # define number of pages
        self.numpages = self.getnumberofpages()
        # iterate through pages and create a list with their raw contents
        self.rawexpenses = [self.getcontentspage(i) for i in range(self.getnumberofpages())]
        self.processed = self.processexpenses()

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

    def processexpenses(self):
        # take the raw expenses
        raw = self.rawexpenses
        # define the header and page splitter
        headerstr = "\nTransaction DateCard UsedTransaction DetailAmount"
        pagesplitter = f' of {self.numpages}'
        # find which page the header is shown
        startpage = [index for index, item in enumerate(raw) if headerstr in item][0]
        result1 = raw[startpage:]
        # remove everything before header
        result2 = [i.split(headerstr)[1] if headerstr in i else i for i in result1]
        # remove everything before the page splitter
        result3 = [i.split(pagesplitter)[1] if pagesplitter in i else i for i in result2]
        # final results
        result = result3
        return result

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
    # [print(i) for i in cc1.rawexpenses]
    print('\n---------------------------------------\n')
    [print(i) for i in cc1.processed]
    print('\n=========================== END OF PROGRAM ==============================--\n')


# main, calling main loop
if __name__ == '__main__':
    main()


