import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility

from eea.climateadapt.testing import \
    EEA_CLIMATEADAPT_INTEGRATION_TESTING
from eea.climateadapt.aceitem import \
    IPublicationReport, IInformationPortal, IGuidanceDocument, \
    ITool, IOrganization


class IntegrationTest(unittest.TestCase):

    layer = EEA_CLIMATEADAPT_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        pid = 'eea.climateadapt'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')

    def test_schema_publication_report(self):
        fti = queryUtility(IDexterityFTI, name='PublicationReport')
        schema = fti.lookupSchema()
        self.assertEqual(IPublicationReport, schema)

    def test_schema_information_potal(self):
        fti = queryUtility(IDexterityFTI, name='IInformationPortal')
        schema = fti.lookupSchema()
        self.assertEqual(IInformationPortal, schema)

    def test_schema_guidance_document(self):
        fti = queryUtility(IDexterityFTI, name='GuidanceDocument')
        schema = fti.lookupSchema()
        self.assertEqual(IGuidanceDocument, schema)

    def test_schema_tool(self):
        fti = queryUtility(IDexterityFTI, name='Tool')
        schema = fti.lookupSchema()
        self.assertEqual(ITool, schema)

    def test_schema_organization(self):
        fti = queryUtility(IDexterityFTI, name='Organization')
        schema = fti.lookupSchema()
        self.assertEqual(IOrganization, schema)
