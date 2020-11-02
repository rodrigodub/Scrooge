# scrooge
# process mastercard PDF
# rodrigo
# 20150407
# v.0.0109

# import os

class FileParse(object):
    def __init__(self, filenamein, filenameout):
        self.filein = filenamein
        self.fileout = filenameout
        self.process(self.filein, self.fileout)
    
    def process(self, filenamein, filenameout):
        # open read file and reads its content
        arqa = open(filenamein, 'r')
        # arqa.readline()
        # open write file and write its content
        arqb = open(filenameout, 'w')
        [arqb.write(SplitMastercard(i).separateString) for i in arqa]
        # closes both
        arqb.close()
        arqa.close()


class SplitMastercard(object):
    def __init__(self, entrada):
        # self.separateAmount = entrada.replace('\n', '').split(' $')
        self.separateAmount = entrada.split(' $')
        try:
            self.separateString = '{}, {}'.format(self.separateAmount[0], self.separateAmount[1])
        except:
            self.separateString = ''


def main():
    # a = '20150127 mastercard.txt'
    # b = '20150407 split.csv'
    a = input('File to process ? ')
    b = input('Resulting file ? ')
    FileParse(a, b)


# main, calling main loop
if __name__ == '__main__':
    # test()
    main()
