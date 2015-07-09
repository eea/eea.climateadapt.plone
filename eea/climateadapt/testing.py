from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class EeaclimateadaptLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import eea.climateadapt
        xmlconfig.file(
            'configure.zcml',
            eea.climateadapt,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'eea.climateadapt:default')

EEA_CLIMATEADAPT_FIXTURE = EeaclimateadaptLayer()
EEA_CLIMATEADAPT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EEA_CLIMATEADAPT_FIXTURE,),
    name="EeaclimateadaptLayer:Integration"
)
EEA_CLIMATEADAPT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EEA_CLIMATEADAPT_FIXTURE, z2.ZSERVER_FIXTURE),
    name="EeaclimateadaptLayer:Functional"
)
