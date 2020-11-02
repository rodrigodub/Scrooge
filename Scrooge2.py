# scrooge
# process mastercard PDF
# rodrigo
# 20201024
# v.1.111

# https://automatetheboringstuff.com/chapter13/

import PyPDF2

FILE_PATH = '20201026a.pdf'

# read PDF
pdfFileObj = open(FILE_PATH, 'rb') 
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
# find and print number of pages
np = pdfReader.numPages
print(f'Number of pages: {np}')
# get the contents of page 1
pageObj = pdfReader.getPage(2)
a = pageObj.extractText() 
print(a)

