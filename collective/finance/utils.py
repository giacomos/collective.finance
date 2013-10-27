# -*- coding: utf-8 -*-
from datetime import datetime
from collective.finance.interfaces import IQIFParser
from zope.interface import implements


def parseQifDateTime(qdate):
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
        iso_date = qdate[6:10] + "-" + qdate[3:5] + "-" + qdate[0:2]
        return datetime.strptime(iso_date, '%Y-%M-%d')
    if qdate[5] == "'":
        C = "20"
    else:
        C = "19"
    iso_date = C + qdate[6:8] + "-" + qdate[3:5] + "-" + qdate[0:2]
    return datetime.strptime(iso_date, '%Y-%M-%d')


class Account(object):

    def __init__(self):
        self.name = None
        self.description = None
        self.account_type = None
        self.credit_limit = None
        self.statement_balance_date = None
        self.statement_balance_amount = None

    def __repr__(self):
        return '<Account: %s>' % self.name


class Category(object):

    def __init__(self):
        self.name = None
        self.description = None
        #Tax related if included, not tax related if omitted
        self.tax_related = None
        self.income_category = None
        self.expense_category = True
        self.budget_amount = None
        self.tax_schedule_info = None

        self.parent_category = None

    def __repr__(self):
        return '<Category: %s>' % self.name


class Transaction(object):
    def __init__(self):
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

    def __repr__(self):
        return "<Transaction units=" + str(self.amount) + ">"


def parseTransaction(chunk):
    """
    """

    curItem = Transaction()
    chunk = chunk.startswith('\n') and chunk[1:] or chunk
    chunk = chunk.endswith('\n') and chunk[:-1] or chunk
    lines = chunk.split('\n')
    for line in lines:
        if not len(line) or line[0] == '\n' or line.startswith('!Type'):
            continue
        elif line[0] == 'D':
            curItem.date = parseQifDateTime(line[1:])
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


def parseAccount(chunk):
    """
    """
    curItem = Account()
    chunk = chunk.startswith('\n') and chunk[1:] or chunk
    chunk = chunk.endswith('\n') and chunk[:-1] or chunk
    lines = chunk.split('\n')
    for line in lines:
        if not len(line) or line[0] == '\n' or line.startswith('!Account'):
            continue
        elif line[0] == 'N':
            curItem.name = line[1:]
        elif line[0] == 'D':
            curItem.description = line[1:]
        elif line[0] == 'T':
            curItem.account_type = line[1:]
        elif line[0] == 'L':
            curItem.credit_limit = line[1:]
        elif line[0] == '/':
            curItem.statement_balance_date = parseQifDateTime(line[1:])
        elif line[0] == '$':
            curItem.credit_limit = line[1:]
        else:
            print 'Line not recognized: ' + line
    return curItem


def parseCategory(chunk):
    """
    """
    curItem = Category()
    chunk = chunk.startswith('\n') and chunk[1:] or chunk
    chunk = chunk.endswith('\n') and chunk[:-1] or chunk
    lines = chunk.split('\n')
    for line in lines:
        if not len(line) or line[0] == '\n' or line.startswith('!Type'):
            continue
        elif line[0] == 'E':
            curItem.expense_category = True
        elif line[0] == 'I':
            curItem.income_category = True
            curItem.expense_category = False  # if ommitted is True
        elif line[0] == 'T':
            curItem.tax_related = True
        elif line[0] == 'D':
            curItem.description = line[1:]
        elif line[0] == 'B':
            curItem.budget_amount = line[1:]
        elif line[0] == 'R':
            curItem.tax_schedule_info = line[1:]
        elif line[0] == 'N':
            full_name = line[1:]
            splitted_name = full_name.split(':')
            name = splitted_name[-1]
            curItem.name = name
            if len(splitted_name) > 1:
                parent = splitted_name[-2]
                curItem.parent_category = parent
    return curItem


class QIFParser(object):

    implements(IQIFParser)

    def parseQIFdata(self, data):
        res = dict.fromkeys(['accounts', 'transactions', 'categories'], [])
        accounts = []
        transactions = []
        chunks = data.split('^')[:-1]
        idx = 0
        account_indexes = []
        account_ops = {}
        for chunk in chunks:
            if '!Account' in chunk:
                account = parseAccount(chunk)
                account_indexes.append(idx)
                accounts.append(account)
            idx += 1
        num = len(accounts)
        ### This can be done better for sure
        categories = [parseCategory(chunk)
                      for chunk in chunks[0:account_indexes[0]]]
        for i in range(num):
            if i < num - 1:
                slice_start = account_indexes[i] + 1
                slice_end = account_indexes[i + 1]
            else:
                slice_start = account_indexes[i] + 1
                slice_end = len(chunks)
            account_ops[accounts[i].name] = chunks[slice_start:slice_end]
        for acc in accounts:
            for op in account_ops[acc.name]:
                tr = parseTransaction(op)
                tr.account = acc.name
                transactions.append(tr)
        res['accounts'] = accounts
        res['transactions'] = transactions
        res['categories'] = categories
        return res
