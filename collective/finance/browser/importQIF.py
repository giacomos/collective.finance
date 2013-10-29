# -*- coding: utf-8 -*-
from z3c.form import (
    form,
    button,
    field
)
from Products.CMFCore.utils import getToolByName
from collective.finance.interfaces import IImportQIFFormSchema
from collective.finance.interfaces import IQIFParser
from collective.finance import messageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility


class ImportQIFView(form.Form):

    """ A sample form showing how to mass import users using
        an uploaded CSV file.
    """

    name = _(u"Import QIF")
    ignoreContext = True
    fields = field.Fields(IImportQIFFormSchema)

    def processAccount(self, context, account):
        title = account.name
        obj_id = context.invokeFactory('FinanceAccount', title)
        obj = self.context[obj_id]
        obj.account_type = account.account_type
        obj.title = title
        obj.reindexObject()
        return obj

    def processCategory(self, context, category):
        title = category.name
        obj_id = context.invokeFactory('FinanceCategory', title)
        obj = self.context[obj_id]
        obj.title = category.name
        if category.income_category:
            obj.income_expense = 'Income'
        obj.parent_category = category.parent_category
        obj.reindexObject()
        return obj

    def processQIF(self, data):
        """
        """

        catalog = getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        brains = catalog(path=path, portal_type="FinanceTransaction")
        num = len(brains)
        ut = getUtility(IQIFParser, name='collective.finance.qifparser')

        struct = ut.parseQIFdata(data)
        acc_uids = {}
        cat_uids = {}
        for account in struct['accounts']:
            obj = self.processAccount(self.context, account)
            acc_uids[obj.title] = obj.UID()
        for category in struct['categories']:
            obj = self.processCategory(self.context, category)
            cat_uids[obj.title] = obj.UID()
        for item in struct['transactions']:
            if not item.date:
                continue
            next_id = 'transaction-%d' % (num + 1)
            num += 1
            if item.to_account:
                obj_id = self.context.invokeFactory('FinanceTransfer',
                                                    next_id)
            else:
                obj_id = self.context.invokeFactory('FinanceTransaction',
                                                    next_id)
            obj = self.context[obj_id]
            obj.date = item.date
            obj.amount = item.amount
            obj.address = item.address
            obj.memo = item.memo
            obj.account = acc_uids[item.account]
            if item.to_account:
                obj.to_account = acc_uids[item.to_account]
            else:
                obj.income_expense = item.amount < 0 and \
                    'Expense' or 'Income'
            next_id = 1
            for split in item.splits:
                split_id = obj.invokeFactory('FinanceAmountSplit',
                                             'split-%d' % next_id)
                split_obj = obj[split_id]
                if split.to_account:
                    split_obj.to_account = acc_uids[split.to_account]
                else:
                    split_obj.income_expense = split.amount < 0 and \
                        'Expense' or 'Income'
                split_obj.amount = split.amount
                split_obj.category = split.category
                split_obj.memo = split.memo
                next_id += 1
#            obj.reindexObject()
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
