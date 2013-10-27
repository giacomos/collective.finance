# -*- coding: utf-8 -*-
import z3c.form.button
import z3c.form
from datetime import datetime
from Products.CMFCore.utils import getToolByName
from collective.finance.interfaces import IImportQIFFormSchema
from collective.finance import messageFactory as _
from Products.statusmessages.interfaces import IStatusMessage


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
        self.order = ['date', 'amount', 'cleared', 'num', 'payee', 'memo',
                      'address', 'category', 'categoryInSplit',
                      'memoInSplit', 'amountOfSplit', 'toAccount']
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


def parseQif(ops):
    """
    Parse a qif file and return a list of entries.
    infile should be open file-like object (supporting readline() ).
    """

    items = []
    curItem = QifItem()
    for op in ops:
        op = op.startswith('\n') and op[1:] or op
        op = op.endswith('\n') and op[:-1] or op
        lines = op.split('\n')
        curItem = QifItem()
        for line in lines:
            if not len(line) or line[0] == '\n' or line.startswith('!Type'):
                continue
            elif line[0] == 'D':
                curItem.date = line[1:]
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
        items.append(curItem)
    return items


def getAccounts(chunks):
    res = []
    idx = 0
    for chunk in chunks:
        if '!Account' in chunk:
            parts = chunk.split('\n')
            account = {}
            account['title'] = parts[2][1:]
            account['type'] = parts[3][1:]
            account['idx'] = idx
            res.append(account)
        idx += 1
    return res


def getTrByAccount(chunks, accounts):
    num = len(accounts)
    for i in range(num):
        if i < num - 1:
            slice_start = accounts[i]['idx'] + 1
            slice_end = accounts[i + 1]['idx']
        else:
            slice_start = accounts[i]['idx'] + 1
            slice_end = len(chunks)
        accounts[i]['ops'] = chunks[slice_start:slice_end]
    return accounts


class ImportQIFView(z3c.form.form.Form):

    """ A sample form showing how to mass import users using
        an uploaded CSV file.
    """

    name = _(u"Import QIF")
    ignoreContext = True
    fields = z3c.form.field.Fields(IImportQIFFormSchema)

    def processQIF(self, data):
        """
        """

        catalog = getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        brains = catalog(path=path, portal_type="FinanceTransaction")
        num = len(brains)

        chunks = data.split('^')
        accounts = getAccounts(chunks)
        accounts = getTrByAccount(chunks, accounts)
        acc_uids = {}
        for account in accounts:
            title = account['title']
            obj_id = self.context.invokeFactory('FinanceAccount', title)
            obj = self.context[obj_id]
            obj.account_type = account['type']
            obj.title = title
            obj.reindexObject()
            acc_uids[title] = obj.UID()
        for account in accounts:
            items = parseQif(account['ops'])

            for item in items:
                if not item.date:
                    continue
                next_id = 'transaction-%d' % (num + 1)
                num += 1
                if item.toAccount:
                    obj_id = self.context.invokeFactory('FinanceTransfer',
                                                        next_id)
                else:
                    obj_id = self.context.invokeFactory('FinanceTransaction',
                                                        next_id)
                obj = self.context[obj_id]
                iso_date = convertDate(item.date)
                obj.date = datetime.strptime(iso_date, '%Y-%M-%d')
                obj.amount = float(item.amount)
                obj.address = item.address
                obj.memo = item.memo
                obj.account = acc_uids[account['title']]
                if item.toAccount:
                    obj.to_account = acc_uids[item.toAccount]
                else:
                    obj.income_expense = item.amount.startswith('-') and \
                        'Expense' or 'Income'
                obj.reindexObject()
        return 'FATTO!!'

    @z3c.form.button.buttonAndHandler(_('Import'), name='import')
    def importQIF(self, action):
        """ Create and handle form button "Import"
        """

        # Extract form field values and errors from HTTP request
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Do magic
        file = data["qif_file"].data

        number = self.processQIF(file)

        # If everything was ok post success note
        # Note you can also use self.status here unless you do redirects
        if number is not None:
            # mark only as finished if we get the new object
            IStatusMessage(self.request).addStatusMessage(
                _(u"Created/updated entries:") + unicode(number), "info")
