""" Async
"""
from zope.interface import Interface


try:
    from plone.app.async.interfaces import IAsyncService
except ImportError:
    class IAsyncService(Interface):
        """ No async """

__all__ = [
    IAsyncService.__name__,
]
