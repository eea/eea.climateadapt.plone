from eea.climateadapt.tiles.search_acecontent import AceTileMixin
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SearchAceContentBlockSerializer(object):
    order = 100
    block_type = "searchAceContent"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):

        ace = AceTileMixin()
        ace.context = self.context
        ace.request = self.request
        ace.data = block
        ace.current_lang = 'en'

        block['_v_results'] = ace.sections()
        # print('sections', block)

        return block
    

@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class RelevantAceContentBlockSerializer(object):
    order = 100
    block_type = "relevantAceContent"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):

        ace = AceTileMixin()
        ace.context = self.context
        ace.request = self.request
        ace.data = block
        ace.current_lang = 'en'

        block['_v_results'] = ace.relevant_all_items()

        return block


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class FilterAceContentBlockSerializer(object):
    order = 100
    block_type = "filterAceContent"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):

        ace = AceTileMixin()
        ace.context = self.context
        ace.request = self.request
        ace.data = block
        ace.current_lang = 'en'

        # import pdb; pdb.set_trace()

        block['_v_results'] = ace.filter_items()

        return block
