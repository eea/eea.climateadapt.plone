"""Pages to deal with workflow"""

import threading

from plone.stringinterp.adapters import BaseSubstitution
from Products.CMFCore.interfaces import IContentish
from zope.component import adapts


MESSAGE_KEY = "cca_indicator_message"
threadlocals = threading.local()


class indicator_message(BaseSubstitution):
    adapts(IContentish)

    category = "CCA Indicator harvest"
    description = "Content of message with modified indicators."

    def safe_call(self):
        message = getattr(threadlocals, MESSAGE_KEY, "#ERROR GETTING MESSAGE")
        return message
