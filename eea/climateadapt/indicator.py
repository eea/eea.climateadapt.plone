""" Pages to deal with workflow
"""

import threading

from plone.stringinterp.adapters import BaseSubstitution
from Products.CMFCore.interfaces import IContentish
from zope.component import adapts
# from zope.component.interfaces import IObjectEvent, ObjectEvent
# from zope.interface import implementer

# from zope.event import notify
# from Products.Five.browser import BrowserView


MESSAGE_KEY = 'cca_indicator_message'
threadlocals = threading.local()


# class IIndicatorMessageEvent(IObjectEvent):
#     """ An event with a message for the workflow transition
#     """

# @implementer(IIndicatorMessageEvent)
# class IndicatorMessageEvent(ObjectEvent):


class indicator_message(BaseSubstitution):
    adapts(IContentish)

    category = 'CCA Indicator harvest'
    description = "Content of message with modified indicators."

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
