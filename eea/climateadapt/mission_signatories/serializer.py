import logging

from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import (
    IBlockFieldSerializationTransformer,
)
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

from mission_signatories import get_discodata_for_mission_signatories


logger = logging.getLogger("eea.climateadapt")


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class MissionSignatoriesProfileBlockSerializater(object):
    order = 100
    block_type = "missionSignatoriesProfile"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        id = block.get('profile_id')
        data = get_discodata_for_mission_signatories(id)
        block["_v_results"] = data
        return block
