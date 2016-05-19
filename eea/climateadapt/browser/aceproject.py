from plone.dexterity.browser.view import DefaultView
from eea.climateadapt.browser import AceViewApi


class AceProjectView(DefaultView, AceViewApi):

    type_label = u"Project"

