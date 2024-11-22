import logging
import os

from plone.api.portal import get_tool
from plone.app.registry.browser.controlpanel import (ControlPanelFormWrapper,
                                                     RegistryEditForm)
from plone.z3cform import layout
from z3c.form import form
from zope.interface import Interface
from zope.schema import Bool, TextLine

logger = logging.getLogger('eea.climateadapt.arcgis')

# FEATURE = "casestudies_pointLayer"

_DEFAULTS = {
    'username': "eea_casestudies",
    'password': os.environ.get('GISPASS', ""),
    'server': "LcQjj2sL7Txk9Lag",
    # 'feature_service': u"casestudies_pointLayer_clone",
    'feature_service': "casestudies_pointLayer",
    'skip_rabbitmq': True,
}


class _defaults:
    """ A hack to return defaults in object form
    """

    def __init__(self):
        self.__dict__.update(_DEFAULTS)


class IArcGISClientSettings(Interface):
    """ Client settings for ArcGIS
    """

    username = TextLine(title="Username", required=True,
                        default=_DEFAULTS['username'])
    password = TextLine(title="Password", required=True)

    server = TextLine(title="Server name",
                      required=True, default=_DEFAULTS['server'])

    feature_service = TextLine(title="Feature Service",
                               required=True,
                               default=_DEFAULTS['feature_service'])

    skip_rabbitmq = Bool(title="Disable message queue",
                         description="Direct processing, without RabbitMQ",
                         required=False, default=False)


class ArcGISClientControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = IArcGISClientSettings


ArcGISClientControlPanelView = layout.wrap_form(
    ArcGISClientControlPanelForm,
    ControlPanelFormWrapper
)
ArcGISClientControlPanelView.label = "ArcGIS Synchronisation settings"


def get_settings():
    try:
        reg = get_tool('portal_registry')
        s = reg.forInterface(IArcGISClientSettings)
    except:     # not in Plone context, return defaults
        logger.info("Couldn't get Plone settings, using defaults")
        s = _defaults()

    return s


def get_endpoint_url(settings=None):
    if settings is None:
        settings = get_settings()

    return "https://services.arcgis.com/{0}/ArcGIS/rest".format(
            settings.server)


def get_feature_url(settings=None):
    if settings is None:
        settings = get_settings()

    endpoint = get_endpoint_url(settings)

    return "{0}/services/{1}/FeatureServer/0".format(
        endpoint, settings.feature_service
    )
