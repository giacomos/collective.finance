# -*- coding: utf-8 -*-
from datetime import datetime
from collective.finance.interfaces import IQIFParser
from zope.interface import implements


def convertDate(qdate):
    """ convert from QIF time format to ISO date string

    QIF is like   "7/ 9/98"  "9/ 7/99"  or   "10/10/99"  or "10/10'01" for y2k
         or, it seems (citibankdownload 20002) like "01/22/2002"
         or, (Paypal 2011) like "3/2/2011".
    ISO is like   YYYY-MM-DD  I think @@check
    """
    if qdate[1] == "/":
        qdate = "0" + qdate   # Extend month to 2 digits
    if qdate[4] == "/":
        qdate = qdate[:3]+"0" + qdate[3:]   # Extend month to 2 digits
    for i in range(len(qdate)):
        if qdate[i] == " ":
            qdate = qdate[:i] + "0" + qdate[i+1:]
    if len(qdate) == 10:  # new form with YYYY date
        return qdate[6:10] + "-" + qdate[0:2] + "-" + qdate[3:5]
    if qdate[5] == "'":
        C = "20"
    else:
        C = "19"
    return C + qdate[6:8] + "-" + qdate[0:2] + "-" + qdate[3:5]


class QifItem(object):
    def __init__(self):
        self.order = ['account', 'date', 'amount', 'cleared',
                      'num', 'payee', 'memo', 'address', 'category',
                      'categoryInSplit', 'memoInSplit',
                      'amountOfSplit', 'toAccount']

        self.account = None
        self.date = None
        self.amount = None
        self.cleared = None
        self.num = None
        self.payee = None
        self.memo = None
        self.address = None
        self.category = None
        self.categoryInSplit = None
        self.memoInSplit = None
        self.amountOfSplit = None
        self.toAccount = None

    def show(self):
        pass

    def __repr__(self):
        titles = ','.join(self.order)
        tmpstring = ','.join([str(self.__dict__[field])
                              for field in self.order])
        tmpstring = tmpstring.replace('None', '')
        return titles + "," + tmpstring

    def dataString(self):
        """
        Returns the data of this QIF without a header row
        """
        tmpstring = ','.join([str(self.__dict__[field])
                             for field in self.order])
        tmpstring = tmpstring.replace('None', '')
        return tmpstring


def parseQIFItem(chunk):
    """
    """

    curItem = QifItem()
    chunk = chunk.startswith('\n') and chunk[1:] or chunk
    chunk = chunk.endswith('\n') and chunk[:-1] or chunk
    lines = chunk.split('\n')
    for line in lines:
        if not len(line) or line[0] == '\n' or line.startswith('!Type'):
            continue
        elif line[0] == 'D':
            date = line[1:]
            iso_date = convertDate(date)
            curItem.date = datetime.strptime(iso_date, '%Y-%M-%d')
        elif line[0] == 'T':
            curItem.amount = line[1:]
        elif line[0] == 'C':
            curItem.cleared = line[1:]
        elif line[0] == 'P':
            curItem.payee = line[1:]
        elif line[0] == 'M':
            curItem.memo = line[1:]
        elif line[0] == 'A':
            curItem.address = line[1:]
        elif line[0] == 'L':
            cat = line[1:]
            if cat.startswith('['):
                curItem.toAccount = cat[1:-1]
            else:
                curItem.category = cat
        elif line[0] == 'S':
            try:
                curItem.categoryInSplit.append(";" + line[1:-1])
            except AttributeError:
                curItem.categoryInSplit = line[1:-1]
        elif line[0] == 'E':
            try:
                curItem.memoInSplit.append(";" + line[1:-1])
            except AttributeError:
                curItem.memoInSplit = line[1:-1]
        elif line[0] == '$':
            try:
                curItem.amountInSplit.append(";" + line[1:-1])
            except AttributeError:
                curItem.amountInSplit = line[1:-1]
        else:
            # don't recognise this line; ignore it
            print ("Skipping unknown line:\n" + str(line))
    return curItem


class QIFParser(object):

    implements(IQIFParser)

    def parseQIFdata(self, data):
        res = dict.fromkeys(['accounts', 'transactions', 'categories'], [])
        accounts = []
        transactions = []
        chunks = data.split('^')
        idx = 0
        for chunk in chunks:
            if '!Account' in chunk:
                parts = chunk.split('\n')
                account = {}
                account['title'] = parts[2][1:]
                account['type'] = parts[3][1:]
                account['idx'] = idx
                accounts.append(account)
            idx += 1
        num = len(accounts)
        for i in range(num):
            if i < num - 1:
                slice_start = accounts[i]['idx'] + 1
                slice_end = accounts[i + 1]['idx']
            else:
                slice_start = accounts[i]['idx'] + 1
                slice_end = len(chunks)
            accounts[i]['ops'] = chunks[slice_start:slice_end]
        for acc in accounts:
            for op in acc['ops']:
                tr = parseQIFItem(op)
                tr.account = acc['title']
                transactions.append(tr)
        res['accounts'] = accounts
        res['transactions'] = transactions
        return res
