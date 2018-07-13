""" Pages to deal with workflow
"""

import threading
from Products.CMFCore.interfaces import IContentish
from plone.stringinterp.adapters import BaseSubstitution
from zope.component import adapts
from zope.component.interfaces import ObjectEvent, IObjectEvent
from zope.event import notify
from zope.interface import implements
from Products.Five.browser import BrowserView


MESSAGE_KEY = 'cca_indicator_message'
threadlocals = threading.local()


class IIndicatorMessageEvent(IObjectEvent):
    """ An event with a message for the workflow transition
    """


class IndicatorMessageEvent(ObjectEvent):
    implements(IIndicatorMessageEvent)


class indicator_message(BaseSubstitution):
    adapts(IContentish)

    category = u'CCA Indicator harvest'
    description = u"Content of message with modified indicators."

    def safe_call(self):
        message = getattr(threadlocals, MESSAGE_KEY, '#ERROR GETTING MESSAGE')
        return message


# class GetIndicator(BrowserView):
#     def render(self):
#         import pdb;pdb.set_trace()
#         notify(IndicatorMessageEvent(self.context))
#         return "render"
#
#     def __call__(self):
#         import pdb;pdb.set_trace()
#         notify(IndicatorMessageEvent(self.context))
#         return "call"

