# -*- coding: utf-8 -*-
from qifparse.parser import QifParser
from StringIO import StringIO
from z3c.form import (
    form,
    button,
    field
)
from collective.finance.interfaces import IImportQIFFormSchema
from collective.finance import messageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from plone.i18n.normalizer import urlnormalizer as normalizer


class ImportQIFView(form.Form):

    """ A sample form showing how to mass import users using
        an uploaded CSV file.
    """

    name = _(u"Import QIF")
    ignoreContext = True
    fields = field.Fields(IImportQIFFormSchema)

    def processAccount(self, context, account):
        title = account.name
        tmpid = normalizer.normalize(title)
        obj_id = context.invokeFactory('FinanceAccount', tmpid)
        obj = self.context[obj_id]
        obj.account_type = account.account_type
        obj.title = title
        obj.reindexObject()
        return obj

    def processCategory(self, context, category):
        title = category.name
        tmpid = normalizer.normalize(title)
        obj_id = context.invokeFactory('FinanceCategory', tmpid)
        obj = self.context[obj_id]
        obj.title = category.name
        if category.income_category:
            obj.income_expense = 'Income'
#        obj.parent_category = category.parent_category
        obj.reindexObject()
        return obj

    def processTransaction(self, context, item, obj_id):
        if not item.date:
            return
        if item.to_account:
            obj_id = context.invokeFactory('FinanceTransfer',
                                           obj_id)
        else:
            obj_id = context.invokeFactory('FinanceTransaction',
                                           obj_id)
        obj = context[obj_id]
        obj.date = item.date
        obj.amount = item.amount
        obj.address = item.address
        obj.memo = item.memo
        if item.to_account:
            obj.to_account = item.to_account
        else:
            obj.income_expense = item.amount < 0 and \
                'Expense' or 'Income'
        next_id = 1
        for split in item.splits:
            split_id = obj.invokeFactory('FinanceAmountSplit',
                                         'split-%d' % next_id)
            split_obj = obj[split_id]
            if split.to_account:
                split_obj.to_account = split.to_account
            else:
                split_obj.income_expense = split.amount < 0 and \
                    'Expense' or 'Income'
            split_obj.amount = split.amount
            split_obj.category = split.category
            split_obj.memo = split.memo
            next_id += 1
        return obj

    def processQIF(self, data):
        """
        """

        qif = QifParser.parse(StringIO(data))
        for account in qif.accounts:
            new_acc = self.processAccount(self.context, account)
            num = 1
            if account.name in qif.transactions:
                for tr in qif.transactions[account.name]:
                    self.processTransaction(new_acc, tr, num)
                    num += 1
        for category in qif.categories:
            self.processCategory(self.context, category)
        return 'FATTO!!'

    @button.buttonAndHandler(_('Import'), name='import')
    def importQIF(self, action):
        """ Create and handle form button "Import"
        """

        # Extract form field values and errors from HTTP request
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Do magic
        data = data["qif_file"].data

        number = self.processQIF(data)

        # If everything was ok post success note
        # Note you can also use self.status here unless you do redirects
        if number is not None:
            # mark only as finished if we get the new object
            IStatusMessage(self.request).addStatusMessage(
                _(u"Created/updated entries:") + unicode(number), "info")
