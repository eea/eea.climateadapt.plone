
import logging

from zope.component import queryUtility
from eea.climateadapt.async import IAsyncService

logger = logging.getLogger('eea.climateadapt')


def get_async_service():
        async_service = queryUtility(IAsyncService)

        return async_service
