# -*- coding: utf-8 -*-
import StringIO
import z3c.form.button
import z3c.form
from datetime import datetime
from Products.CMFCore.utils import getToolByName
from collective.finance.interfaces import IImportQIFFormSchema
from collective.finance import messageFactory as _
from Products.statusmessages.interfaces import IStatusMessage


class QifItem(object):
    def __init__(self):
        self.order = ['date', 'amount', 'cleared', 'num', 'payee', 'memo',
                      'address', 'category', 'categoryInSplit',
                      'memoInSplit', 'amountOfSplit']
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


def parseQif(infile):
    """
    Parse a qif file and return a list of entries.
    infile should be open file-like object (supporting readline() ).
    """

    items = []
    curItem = QifItem()
    line = infile.readline()
    while line != '':
        if line[0] == '\n':  # blank line
            pass
        elif line[0] == '^':  # end of item
            # save the item
            items.append(curItem)
            curItem = QifItem()
        elif line[0] == 'D':
            curItem.date = line[1:-1]
        elif line[0] == 'T':
            curItem.amount = line[1:-1]
        elif line[0] == 'C':
            curItem.cleared = line[1:-1]
        elif line[0] == 'P':
            curItem.payee = line[1:-1]
        elif line[0] == 'M':
            curItem.memo = line[1:-1]
        elif line[0] == 'A':
            curItem.address = line[1:-1]
        elif line[0] == 'L':
            curItem.category = line[1:-1]
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
            print ("Skipping unknown line:\n" + line)

        line = infile.readline()
    return items


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
        io = StringIO.StringIO(data)
        items = parseQif(io)
        catalog = getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        brains = catalog(path=path, portal_type="FinanceTransaction")
        num = len(brains)
        for item in items:
            next_id = 'transaction-%d' % (num + 1)
            num += 1
            obj_id = self.context.invokeFactory('FinanceTransaction', next_id)
            obj = self.context[obj_id]
            obj.date = datetime.strptime(item.date, '%d/%M/%Y')
            obj.amount = float(item.amount)
            obj.address = item.address
            obj.memo = item.memo
            obj.income_expense = item.amount.startswith('-') and 'Expense' \
                or 'Income'
            import pdb; pdb.set_trace()
        return len(items)

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
