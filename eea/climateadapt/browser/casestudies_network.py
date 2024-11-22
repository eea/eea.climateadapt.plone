from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from eea.climateadapt.browser import AceViewApi
from plone.dexterity.browser.view import DefaultView
from plone import api

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import lxml.html
import json
import logging
from plone.api.portal import get_tool

logger = logging.getLogger("eea.climateadapt")


class Network(BrowserView):

    #def __call__(self):
    def get_data(self):
        """"""
        factory = getUtility(IVocabularyFactory, 'eea.climateadapt.aceitems_climateimpacts')
        vocabulary_impacts = factory(self.context)
        factory = getUtility(IVocabularyFactory, "eea.climateadapt.aceitems_sectors")
        vocabulary_sectors = factory(self.context)

        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults(
            {
                "portal_type": [
                    "eea.climateadapt.casestudy"
                ],
                "review_state": "published"
            }
        )
        sectors = {}
        impacts = {}

        edges_index = {}

        nodes = []
        edges = []
        for brain in brains:
            if len(nodes)>50:
                break
            case_study_index = len(nodes)
            obj = brain.getObject()
            #nodes.append({
            #    'id': case_study_index,
            #    'title': obj.title.encode("utf-8"),
            #    'group': 'gr_case_study',
            #    'value': len(obj.sectors) + len(obj.climate_impacts)
            #    })
            #import pdb; pdb.set_trace()

            for sector_name in obj.sectors:
                index = len(nodes)
                if sector_name not in list(sectors.keys()):
                    sectors[sector_name] = index
                    nodes.append({
                        'id': index,
                        'title': sector_name.encode("utf-8"),
                        'group': 'gr_sector',
                        'value': 0
                        })
                else:
                    index = sectors[sector_name]
                nodes[index]['value'] = nodes[index]['value'] +1
                #edges.append({'from': case_study_index, 'to': index})
            for impact_name in obj.climate_impacts:
                index = len(nodes)
                if impact_name not in list(impacts.keys()):
                    nodes.append({
                        'id': index,
                        'title': impact_name.encode("utf-8"),
                        'group': 'gr_impact',
                        'value': 0
                        })
                    impacts[impact_name] = index
                else:
                    index = impacts[impact_name]
                nodes[index]['value'] = nodes[index]['value'] +1
                #edges.append({'from': case_study_index, 'to': index})
            #import pdb; pdb.set_trace()

            for sector_name in obj.sectors:
                for impact_name in obj.climate_impacts:
                    index_name = sector_name + '_' + impact_name
                    if index_name not in edges_index:
                        edges_index[index_name] = len(edges)
                        edges.append({'from': sectors[sector_name], 'to': impacts[impact_name], 'value': 0})

                    index = edges_index[index_name]
                    edges[index]['value'] = edges[index]['value'] + 1
        return {'nodes': nodes, 'edges': edges}
        #import pdb; pdb.set_trace()


class Sankey(BrowserView):

    #def __call__(self):
    def get_data(self):
        """"""

        factory = getUtility(IVocabularyFactory, 'eea.climateadapt.aceitems_climateimpacts')
        vocabulary_impacts = factory(self.context)
        factory = getUtility(IVocabularyFactory, "eea.climateadapt.aceitems_sectors")
        vocabulary_sectors = factory(self.context)

        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults(
            {
                "portal_type": [
                    "eea.climateadapt.casestudy"
                ],
                "review_state": "published"
            }
        )
        sectors = {}
        impacts = {}

        edges_index = {}

        nodes = []
        edges = []
        for brain in brains:
            obj = brain.getObject()
            for sector_name in obj.sectors:
                for impact_name in obj.climate_impacts:
                    if impact_name == 'NONSPECIFIC' and sector_name == 'NONSPECIFIC':
                        continue
                    index_name = sector_name + '_' + impact_name
                    if index_name not in edges_index:
                        edges_index[index_name] = len(edges)
                        edges.append([sector_name.encode("utf-8"), impact_name.encode("utf-8"), 0])

                    index = edges_index[index_name]
                    edges[index][2] = edges[index][2] + 1


        #import pdb; pdb.set_trace()
        return edges


class Items(BrowserView):

    def __call__(self):
        """"""

        factory = getUtility(IVocabularyFactory, 'eea.climateadapt.aceitems_climateimpacts')
        vocabulary_impacts = factory(self.context)
        factory = getUtility(IVocabularyFactory, "eea.climateadapt.aceitems_sectors")
        vocabulary_sectors = factory(self.context)

        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults(
            {
                "portal_type": [
                    "eea.climateadapt.casestudy"
                ],
                "review_state": "published"
            }
        )
        index_sectors = {}
        index_impacts = {}
        index_ipcc_categories = {}

        edges_index = {}

        nodes = []
        edges = []
        items = []

        for brain in brains:
            #if len(nodes)>50:
            #    break
            case_study_index = len(nodes)
            obj = brain.getObject()
            print(brain.getURL)
            list_ipcc_categories = []
            adaptation_options = obj.adaptationoptions
            for ao_related in adaptation_options:
                try:
                    ao = ao_related.to_object
                    if hasattr(ao, 'ipcc_category'):
                        for ipcc_category in ao.ipcc_category:
                            if ipcc_category not in list_ipcc_categories:
                                list_ipcc_categories.append(ipcc_category)
                            if ipcc_category not in index_ipcc_categories:
                                index_ipcc_categories[ipcc_category] = len(nodes)
                                nodes.append({
                                    'id': ipcc_category.encode("utf-8")
                                    })
                except:
                    ''

            items.append({
                "id": brain.UID,
                "title": obj.title,
                "url": brain.getURL(),
                "sectors": obj.sectors,
                "impacts": obj.climate_impacts,
                "ipcc_categories": list_ipcc_categories
            })

            for sector_name in obj.sectors:
                if sector_name == 'NONSPECIFIC':
                    continue
                print('---S:'+sector_name)
                if sector_name not in list(index_sectors.keys()):
                    index_sectors[sector_name] = len(nodes)
                    nodes.append({
                        'id': sector_name.encode("utf-8")
                        })
            for impact_name in obj.climate_impacts:
                if impact_name == 'NONSPECIFIC':
                    continue
                print('---I:'+impact_name)
                if impact_name not in list(index_impacts.keys()):
                    index_impacts[impact_name] = len(nodes)
                    nodes.append({
                        'id': impact_name.encode("utf-8")
                        })

            for sector_name in obj.sectors:
                for impact_name in obj.climate_impacts:
                    if impact_name == 'NONSPECIFIC' or sector_name == 'NONSPECIFIC':
                        continue
                    index_name = sector_name + '_' + impact_name
                    if index_name not in edges_index:
                        edges_index[index_name] = len(edges)
                        edges.append({'source': sector_name.encode("utf-8"), 'target': impact_name.encode("utf-8"), 'value': 0})

                    index = edges_index[index_name]
                    edges[index]['value'] = edges[index]['value'] + 1
                for impact_name in obj.climate_impacts:
                    if impact_name == 'NONSPECIFIC':
                        continue
                    for ipcc_category in list_ipcc_categories:
                        index_name = impact_name + '_' + ipcc_category
                        if index_name not in edges_index:
                            edges_index[index_name] = len(edges)
                            edges.append({'source': impact_name.encode("utf-8"), 'target': ipcc_category.encode("utf-8"), 'value': 0})

                        index = edges_index[index_name]
                        edges[index]['value'] = edges[index]['value'] + 1

        print(index_ipcc_categories)
        print(index_impacts)
        print(index_sectors)
        response = self.request.response
        response.setHeader('Content-type', 'application/json')

        return json.dumps({'nodes': nodes, 'links': edges, 'items': items})


class Plotly(BrowserView):

    def __call__(self):
        """"""
        results = self.compute()
        response = self.request.response
        response.setHeader('Content-type', 'application/json')

        return json.dumps(results)

    def get_data(self):
        """"""
        results = self.compute()

        #import pdb; pdb.set_trace()
        return json.dumps(results)

    def compute(self):
        """"""
        factory = getUtility(IVocabularyFactory, 'eea.climateadapt.aceitems_climateimpacts')
        vocabulary_impacts = factory(self.context)
        factory = getUtility(IVocabularyFactory, "eea.climateadapt.aceitems_sectors")
        vocabulary_sectors = factory(self.context)
        factory = getUtility(IVocabularyFactory, "eea.climateadapt.aceitems_ipcc_category")
        vocabulary_ipcc_category = factory(self.context)

        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults(
            {
                "portal_type": [
                    "eea.climateadapt.casestudy"
                ],
                "review_state": "published"
            }
        )
        indexes = {
                'nodes':{},
                'sectors':{},
                'ipcc_categories': {},
                'ipcc_values': {},
                'impacts':{}
            }
        filter_choices = {
                'sectors':[],
                'impacts':[],
                'ipcc':{},
            }

        edges_index = {}

        nodes = []
        edges = []
        items = []
        sources = []
        targets = []
        values  = []


        ipcc_have_data = {'yes':0,'no':0,'err':0,'ao':0,'ipcc':0}
        for brain in brains:
            #if len(nodes)>50:
            #    break
            case_study_index = len(nodes)
            obj = brain.getObject()
#            print(brain.getURL)
            list_ipcc_categories = {}
            list_ipcc_values = []
            adaptation_options = obj.adaptationoptions
            if len(adaptation_options)>0:
                ipcc_have_data['yes'] = ipcc_have_data['yes'] +1
            else:
                ipcc_have_data['no'] = ipcc_have_data['no'] +1
            ipcc_have_data['ao'] = ipcc_have_data['ao'] + len(adaptation_options)

            for ao_related in adaptation_options:
                try:
                    ao = ao_related.to_object
                    if hasattr(ao, 'ipcc_category'):
                        #import pdb; pdb.set_trace()
                        print('=============')
                        for ipcc in ao.ipcc_category:
                            ipcc_have_data['ipcc'] = ipcc_have_data['ipcc'] +1
                            name = vocabulary_ipcc_category.getTerm(ipcc).title
                            name_arr = name.split(': ')
                            name_category = name_arr[0]
                            name_value = name_arr[1]
                            print(name_category+':'+name_value)
                            if name_category not in list(indexes['nodes'].keys()):
                                #indexes['ipcc_categories'][name_category] = len(nodes)
                                indexes['nodes'][name_category] = len(nodes)
                                nodes.append(name_category)
                                filter_choices['ipcc'][name_category] = []
                            if name_value not in list(indexes['nodes'].keys()):
                                #indexes['ipcc_values'][name_value] = len(nodes)
                                indexes['nodes'][name_value] = len(nodes)
                                nodes.append(name_value)
                                filter_choices['ipcc'][name_category].append(name_value)

                            if name_category not in list_ipcc_categories:
                                list_ipcc_categories[name_category] = []
                            if name_value not in list_ipcc_categories[name_category]:
                                list_ipcc_categories[name_category].append(name_value)
                                list_ipcc_values.append(name_value)
                        #import pdb; pdb.set_trace()
                except Exception as e:
                    ipcc_have_data['err'] = ipcc_have_data['err'] +1

                    logger.error('Failed: '+ str(e))
                    print(brain.getURL())

            tag = lxml.etree.fromstring('<p>'+obj.long_description.raw.encode('utf-8').decode('utf-8')+'</p>')
            lxml.etree.strip_tags(tag, '*')
            #import pdb; pdb.set_trace()
            item = {
                "id": brain.UID,
                "title": obj.title,
                "description": lxml.etree.tostring(tag),
                "url": brain.getURL(),
                "sectors": [vocabulary_sectors.getTerm(name).title for name in obj.sectors],
                "impacts": [vocabulary_impacts.getTerm(name).title for name in obj.climate_impacts],
                "ipccs": list_ipcc_values
            }
            item['description'] = item['description'][3:-4][0:200]
            items.append(item);

            # Create sectors choises and index
            for sector_name in obj.sectors:
                if sector_name == 'NONSPECIFIC':
                    continue
                name = vocabulary_sectors.getTerm(sector_name).title
                if name not in filter_choices['sectors']:
                    filter_choices['sectors'].append(name)
                if sector_name not in list(indexes['sectors'].keys()):
                    indexes['sectors'][sector_name] = len(nodes)
                    indexes['nodes'][sector_name] = len(nodes)
                    nodes.append(name)

            # Create impacts choises and index
            for impact_name in obj.climate_impacts:
                if impact_name == 'NONSPECIFIC':
                    continue
                name = vocabulary_impacts.getTerm(impact_name).title
                #impact_name.encode("utf-8")
                if name not in filter_choices['impacts']:
                    filter_choices['impacts'].append(name)
                if impact_name not in list(indexes['impacts'].keys()):
                    indexes['impacts'][impact_name] = len(nodes)
                    indexes['nodes'][impact_name] = len(nodes)
                    nodes.append(name)

            # Create edges sector->impact
            for sector_name in obj.sectors:
                if impact_name == 'NONSPECIFIC':
                    continue
                for impact_name in obj.climate_impacts:
                    if sector_name == 'NONSPECIFIC':
                        continue
                    index_name = sector_name + '_' + impact_name
                    if index_name not in edges_index:
                        edges_index[index_name] = len(edges)
                        edges.append({'source': sector_name, 'target': impact_name, 'value': 0})

                    index = edges_index[index_name]
                    edges[index]['value'] = edges[index]['value'] + 1

            # Create edges impact->adaptation option
            for impact_name in obj.climate_impacts:
                if impact_name == 'NONSPECIFIC':
                    continue

                for ipcc_category in list_ipcc_categories:
                    #import pdb; pdb.set_trace()
                    index_name = impact_name + '_' + ipcc_category
                    if index_name not in edges_index:
                        edges_index[index_name] = len(edges)
                        edges.append({
                            'source': impact_name,
                            'target': ipcc_category,
                            'value': 0
                            })

                    index = edges_index[index_name]
                    edges[index]['value'] = edges[index]['value'] + 1
                    for ipcc_value in list_ipcc_categories[ipcc_category]:
                        index_name = ipcc_category + '_' + ipcc_value
                        if index_name not in edges_index:
                            edges_index[index_name] = len(edges)
                            edges.append({
                                'source': ipcc_category,
                                'target': ipcc_value,
                                'value': 0
                                })

                        index = edges_index[index_name]
                        edges[index]['value'] = edges[index]['value'] + 1

        for edge in edges:
            sources.append(indexes['nodes'][edge['source']]);
            targets.append(indexes['nodes'][edge['target']]);
            values.append(edge['value']);

        data = {
            'filters': filter_choices,
            'nodes': nodes,
            'sources': sources,
            'targets': targets,
            'values':values,
            'items': items
        }

        print(ipcc_have_data)
        #import pdb; pdb.set_trace()
        return data;
