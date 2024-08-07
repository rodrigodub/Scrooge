#########################################################################################
# Scrooge
# Automation of Mastercard statement .data extraction and classification
# Author: Rodrigo Nobrega
# 20150407-20201105
#
# Usage:
# $ python3 scrooge.py
#########################################################################################
__version__ = 1.119


# import libraries
import PyPDF2
import pandas as pd


# global variables
FILE_PATH = '20190226a.pdf'
# FILE_PATH = '20201026a.pdf'
EXCEPTIONS = ['OPENING BALANCE', 'HSBC BANK PAYMENT', 'CLOSING BALANCE', 'ORIGINAL TRANSACTION AMOUNT', 'OVERSEAS TRANSACTION FEE']


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
        # 1. take the raw expenses
        raw = self.rawexpenses
        # 2. define the splitter strings
        headerstr = "\nTransaction DateCard UsedTransaction DetailAmount"
        pagesplitter = f" of {self.numpages}"
        endsplitter = "+--= Rewards Points Summary"
        # 3. find which page the header is shown
        startpage = [index for index, item in enumerate(raw) if headerstr in item][0]
        result1 = raw[startpage:]
        # 4. take only the relevant parts
        # 4.1. remove everything before header
        result2 = [i.split(headerstr)[1] if headerstr in i else i for i in result1]
        # 4.2. remove everything before the page splitter
        result3 = [i.split(pagesplitter)[1] if pagesplitter in i else i for i in result2]
        # 4.3. remove everything after the last expenses
        result4 = [i.split(endsplitter)[0] if endsplitter in i else i for i in result3]
        result4 = [i for i in result4 if i]
        # 5. create new list with individual expenses
        result5 = []
        initial = 0
        # 5.1. iterate through original strings
        for page in result4:
            # 5.2. find the indexes to split.
            #      Positions of '.' plus 2 'cents' digits. Except the last position
            indexes = [i + 3 for i in range(len(page)) if page.startswith('.', i)][:-1]
            # 5.3. iterate the string to build final list
            for idx in indexes:
                result5.append(page[initial:idx])
                initial = idx
            # 5.4. append the last activity
            result5.append(page[indexes[-1:][0]:])
        # 6. concatenate broken lines
        result6 = []
        lineprefix = ''
        for item in result5:
            # cases: a) with '.COM', b) with 'HELP.'
            if item[-3:] == '.CO' or item[-7:-2] == 'HELP.':
                lineprefix = item
            else:
                if item:
                    result6.append(lineprefix + item)
                lineprefix = ''
        # 7. skip exceptions
        result7 = result6.copy()
        for item in result7:
            for exc in EXCEPTIONS:
                if exc in item:
                    result7.remove(item)
        # 7. skip exceptions
        result8 = result7.copy()
        for item in result8:
            for exc in EXCEPTIONS:
                if exc in item:
                    result8.remove(item)
        # final results
        result = result8
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


