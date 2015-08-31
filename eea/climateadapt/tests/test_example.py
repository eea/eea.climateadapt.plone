import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility
from plone.app.testing import setRoles, TEST_USER_ID

from eea.climateadapt.testing import \
    EEA_CLIMATEADAPT_INTEGRATION_TESTING
from eea.climateadapt.aceitem import \
    IPublicationReport, IInformationPortal, IGuidanceDocument, \
    ITool, IOrganization
from eea.climateadapt.acemeasure import ICaseStudy, IAdaptationOption
from eea.climateadapt.aceproject import IAceProject


class IntegrationTest(unittest.TestCase):

    layer = EEA_CLIMATEADAPT_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        pid = 'eea.climateadapt'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')

    def test_schema_publication_report(self):
        fti = queryUtility(IDexterityFTI,
                           name='eea.climateadapt.publicationreport')
        schema = fti.lookupSchema()
        self.assertEqual(IPublicationReport, schema)

    def test_add_publication_report(self):
        self.portal.invokeFactory('eea.climateadapt.publicationreport',
                                  'publication_report')
        self.assertTrue(
            IPublicationReport.providedBy(self.portal.publication_report))

    def test_schema_information_portal(self):
        fti = queryUtility(IDexterityFTI,
                           name='eea.climateadapt.informationportal')
        schema = fti.lookupSchema()
        self.assertEqual(IInformationPortal, schema)

    def test_add_information_portal(self):
        self.portal.invokeFactory('eea.climateadapt.informationportal',
                                  'information_portal')
        self.assertTrue(
            IInformationPortal.providedBy(self.portal.information_portal))

    def test_schema_guidance_document(self):
        fti = queryUtility(IDexterityFTI,
                           name='eea.climateadapt.guidancedocument')
        schema = fti.lookupSchema()
        self.assertEqual(IGuidanceDocument, schema)

    def test_add_guidance_document(self):
        self.portal.invokeFactory('eea.climateadapt.guidancedocument',
                                  'guidance_document')
        self.assertTrue(
            IGuidanceDocument.providedBy(self.portal.guidance_document))

    def test_schema_tool(self):
        fti = queryUtility(IDexterityFTI, name='eea.climateadapt.tool')
        schema = fti.lookupSchema()
        self.assertEqual(ITool, schema)

    def test_add_tool(self):
        self.portal.invokeFactory('eea.climateadapt.tool', 'tool')
        self.assertTrue(ITool.providedBy(self.portal.tool))

    def test_schema_organization(self):
        fti = queryUtility(IDexterityFTI, name='eea.climateadapt.organization')
        schema = fti.lookupSchema()
        self.assertEqual(IOrganization, schema)

    def test_add_organization(self):
        self.portal.invokeFactory('eea.climateadapt.organization',
                                  'organization')
        self.assertTrue(IOrganization.providedBy(self.portal.organization))

    def test_schema_casestudy(self):
        fti = queryUtility(IDexterityFTI, name='eea.climateadapt.casestudy')
        schema = fti.lookupSchema()
        self.assertEqual(ICaseStudy, schema)

    def test_add_casestudy(self):
        self.portal.invokeFactory('eea.climateadapt.casestudy',
                                  'case_study')
        self.assertTrue(ICaseStudy.providedBy(self.portal.case_study))

    def test_schema_adaptationoption(self):
        fti = queryUtility(IDexterityFTI,
                           name='eea.climateadapt.adaptationoption')
        schema = fti.lookupSchema()
        self.assertEqual(IAdaptationOption, schema)

    def test_add_adaptationoption(self):
        self.portal.invokeFactory('eea.climateadapt.adaptationoption',
                                  'adaptation_option')
        self.assertTrue(
            IAdaptationOption.providedBy(self.portal.adaptation_option))

    def test_schema_aceproject(self):
        fti = queryUtility(IDexterityFTI, name='eea.climateadapt.aceproject')
        schema = fti.lookupSchema()
        self.assertEqual(IAceProject, schema)

    def test_add_aceproject(self):
        self.portal.invokeFactory('eea.climateadapt.aceproject',
                                  'ace_project')
        self.assertTrue(
            IAceProject.providedBy(self.portal.ace_project))
