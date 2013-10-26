# -*- coding: utf-8 -*-
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import login

from plone.testing import z2

from zope.configuration import xmlconfig


class CollectiveFinance(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.finance
        xmlconfig.file(
            'configure.zcml',
            collective.finance,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.finance:default')
        portal.acl_users.userFolderAddUser('admin',
                                           'secret',
                                           ['Manager'],
                                           [])
        login(portal, 'admin')
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory(
            "Folder",
            id="robot-test-folder",
            title=u"Test Folder"
        )

    def tearDownPloneSite(self, portal):
        applyProfile(portal, 'collective.finance:uninstall')


COLLECTIVE_FINANCE_FIXTURE = CollectiveFinance()
COLLECTIVE_FINANCE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_FINANCE_FIXTURE,),
    name="CollectiveFinance:Integration"
)
COLLECTIVE_FINANCE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_FINANCE_FIXTURE,),
    name="CollectiveFinance:Functional"
)
COLLECTIVE_FINANCE_ROBOT_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_FINANCE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="CollectiveFinance:Robot"
)
