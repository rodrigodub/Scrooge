# scrooge
# process mastercard PDF
# rodrigo
# 20201024
# v.1.110

# https://www.soudegesu.com/en/post/python/open-pdf-with-pypdf2/

import PyPDF2

FILE_PATH = '20201026a.pdf'

with open(FILE_PATH, mode='rb') as f:        
    reader = PyPDF2.PdfFileReader(f)
    print(f"Number of pages: {reader.getNumPages()}")