# -*- coding: utf-8 -*-
from datetime import datetime
from collective.finance.interfaces import IQIFParser
from zope.interface import implements

NON_INVST_ACCOUNT_TYPES = [
    '!Type:Cash',
    '!Type:Bank',
    '!Type:Ccard',
    '!Type:Oth A',
    '!Type:Oth L',
    '!Type:Invoice',  # Quicken for business only
]


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


class AmountSplit(object):
    def __init__(self):
        self.category = None
        self.amount = None
        self.memo = None

        self.toAccount = None


class Transaction(object):
    def __init__(self):
        self.account = None
        self.toAccount = None
        self.splits = []

        self.date = None
        self.amount = None
        self.cleared = None
        self.num = None
        self.payee = None
        self.memo = None
        self.address = None
        self.category = None
#        self.categoryInSplit = None
#        self.memoInSplit = None
#        self.amountOfSplit = None

    def __repr__(self):
        return "<Transaction units=" + str(self.amount) + ">"


class Investment(object):
    def __init__(self):
        self.account = None
        self.toAccount = None  # L, account for a trasnfer

        self.date = None  # D, date
        self.action = None  # N, investment action
        self.security = None  # Y, security name
        self.price = None  # I, price
        self.quantity = None  # Q, quantity
        self.cleared = None  # C, cleared status
        self.amount = None  # T, amount
        self.memo = None  # M, memo
        self.first_line = None  # P, text in the first line
        self.amount_transfer = None  # $, amount for a transfer
        self.commission = None  # O, commission_cost

    def __repr__(self):
        return "<Investment units=" + str(self.amount) + ">"


def parseInvestment(chunk):
    """
    """

    curItem = Investment()
    lines = chunk.split('\n')
    for line in lines:
        if not len(line) or line[0] == '\n' or line.startswith('!Type'):
            continue
        elif line[0] == 'D':
            curItem.date = parseQifDateTime(line[1:])
        elif line[0] == 'T':
            curItem.amount = float(line[1:])
        elif line[0] == 'N':
            curItem.action = line[1:]
        elif line[0] == 'Y':
            curItem.security = line[1:]
        elif line[0] == 'I':
            curItem.price = line[1:]
        elif line[0] == 'Q':
            curItem.quantity = line[1:]
        elif line[0] == 'C':
            curItem.cleared = line[1:]
        elif line[0] == 'M':
            curItem.memo = line[1:]
        elif line[0] == 'P':
            curItem.first_line = line[1:]
        elif line[0] == 'L':
            curItem.toAccount = line[2:-1]
        elif line[0] == '$':
            curItem.amount_transfer = float(line[1:])
        elif line[0] == 'O':
            curItem.commission = float(line[1:])
    return curItem


def parseTransaction(chunk):
    """
    """

    curItem = Transaction()
    lines = chunk.split('\n')
    for line in lines:
        if not len(line) or line[0] == '\n' or line.startswith('!Type'):
            continue
        elif line[0] == 'D':
            curItem.date = parseQifDateTime(line[1:])
        elif line[0] == 'T':
            curItem.amount = float(line[1:])
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
            curItem.splits.append(AmountSplit())
            split = curItem.splits[-1]
            cat = line[1:]
            if cat.startswith('['):
                split.toAccount = cat[1:-1]
            else:
                split.category = cat
        elif line[0] == 'E':
            split = curItem.splits[-1]
            split.memo = line[1:-1]
        elif line[0] == '$':
            split = curItem.splits[-1]
            split.amount = float(line[1:-1])
        else:
            # don't recognise this line; ignore it
            print ("Skipping unknown line:\n" + str(line))
    return curItem


def parseAccount(chunk):
    """
    """
    curItem = Account()
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


class QifParserException(Exception):
    pass


class QIFParser(object):

    implements(IQIFParser)

    def parseQIFdata(self, data):
        if len(data) == 0:
            raise QifParserException('Data is empty')
        res = {
            'accounts': [],
            'transactions': [],
            'categories': [],
            'investments': []
        }
        chunks = data.split('\n^\n')
        last_type = None
        parsers = {
            'categories': parseCategory,
            'accounts': parseAccount,
            'transactions': parseTransaction,
            'investments': parseInvestment
        }
        for chunk in chunks:
            if chunk.startswith('!Type:Cat'):
                last_type = 'categories'
            elif chunk.startswith('!Account'):
                last_type = 'accounts'
            elif chunk.split('\n')[0] in NON_INVST_ACCOUNT_TYPES:
                last_type = 'transactions'
            elif chunk.startswith('!Type:Invst'):
                last_type = 'investments'
            elif chunk.startswith('!Type:Class'):
                continue  # yet to be done!
            elif chunk.startswith('!Type:Memorized'):
                continue  # yet to be done!
            elif chunk.startswith('!'):
                raise QifParserException('Header not reconized')
            # if no header is recognized then
            # we use the previous one
            parsed_item = parsers[last_type](chunk)
            res[last_type].append(parsed_item)
        return res
