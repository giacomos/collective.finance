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

    def processQIF(self, data):
        """
        """

        catalog = getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        brains = catalog(path=path, portal_type="FinanceTransaction")
        ut = getUtility(IQIFParser, name='collective.finance.qifparser')
        num = len(brains)

        struct = ut.parseQIFdata(data)
        acc_uids = {}
        for account in struct['accounts']:
            title = account['title']
            obj_id = self.context.invokeFactory('FinanceAccount', title)
            obj = self.context[obj_id]
            obj.account_type = account['type']
            obj.title = title
            obj.reindexObject()
            acc_uids[title] = obj.UID()
        for item in struct['transactions']:
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
            obj.date = item.date
            obj.amount = float(item.amount)
            obj.address = item.address
            obj.memo = item.memo
            obj.account = acc_uids[item.account]
            if item.toAccount:
                obj.to_account = acc_uids[item.toAccount]
            else:
                obj.income_expense = item.amount.startswith('-') and \
                    'Expense' or 'Income'
            obj.reindexObject()
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
        file = data["qif_file"].data

        number = self.processQIF(file)

        # If everything was ok post success note
        # Note you can also use self.status here unless you do redirects
        if number is not None:
            # mark only as finished if we get the new object
            IStatusMessage(self.request).addStatusMessage(
                _(u"Created/updated entries:") + unicode(number), "info")
