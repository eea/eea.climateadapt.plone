""" A command line ArcGIS client

Call it from a script such as:

    #!/bin/bash
    export LD_LIBRARY_PATH=../../../../../parts/gdal-compile/lib
    export GISPASS=mypass
    ../../../../../bin/zopepy sync_to_arcgis.py "$@"

This commands accepts various parameter. Look at __main__ to see what it does.

# TODO: this script is hackish. Maybe optparse would improve feeling.
"""

import json
import sys

from eea.climateadapt.sat.arcgis import (_get_obj_FID, apply_edits,
                                         get_auth_token, query_layer)
from eea.climateadapt.sat.settings import get_feature_url
from lxml.etree import Element, SubElement, fromstring, tostring


def backup_data(data, path='out.xml'):
    """ Makes an XML backup data from existing data in ArcGIS
    """
    root = Element("casestudies")

    for cs in data:
        e_cs = SubElement(root, 'casestudy')
        e_attrs = SubElement(e_cs, 'attributes')

        for k, v in cs['attributes'].items():
            el = Element(k)
            el.text = unicode(v)
            e_attrs.append(el)
        e_geo = SubElement(e_cs, 'geometry')

        for k, v in cs['geometry'].items():
            el = Element(k)
            el.text = unicode(v)
            e_geo.append(el)

    with open(path, 'w') as f:
        out = tostring(root, pretty_print=True)
        f.write(out)


def delete_casestudy(fid, token):
    """ Delete a casestudy. To be used from command line
    """

    return apply_edits(fid, op='deletes', token=token)


def delete_all_casestudies(token):
    res = query_layer(token)
    all_ids = [x['attributes']['FID'] for x in res['features']]

    return apply_edits(all_ids, op='deletes', token=token)


def add_casestudy(entry):
    """ Add a casestudy to ArgGIS
    """
    # return apply_edits(entry, op='deletes', token=token)


def parse_dump(path):

    with open(path) as f:
        txt = f.read()

    entries = []
    root = fromstring(txt)

    for e_cs in root.xpath('//casestudy'):
        e = {'geometry': {}, 'attributes': {}}
        e_attrs = e_cs.find('attributes')
        e_geo = e_cs.find('geometry')

        for c in e_attrs.iterchildren():
            e['attributes'][c.tag] = (c.text or "").strip()

        for c in e_geo.iterchildren():
            e['geometry'][c.tag] = float(c.text.strip())

        entries.append(e)

    return entries


def edit_casestudy(fid, path, token):
    """ Used from command line
    """

    entries = parse_dump(path)
    entry = None

    for e in entries:
        if e['attributes']['FID'] == fid:
            entry = e

            break

    assert entry
    desc = entry['attributes']['desc_']
    html = fromstring(desc)
    desc = tostring(html, encoding='utf-8', method='text').strip()
    entry['attributes']['desc_'] = desc
    res = apply_edits(json.dumps([entry]), op='updates', token=token)

    assert 'error' not in res

    return res


def add_all_casestudies(path, token):
    """ Used from command line
    """
    entries = parse_dump(path)

    # need to escape html

    for entry in entries:
        desc = entry['attributes']['desc_']
        html = fromstring(desc)
        desc = tostring(html, encoding='utf-8', method='text').strip()
        entry['attributes']['desc_'] = desc

    res = apply_edits(json.dumps(entries), op='adds', token=token)

    return res


def main():
    # Needs env vars:
    #     LD_LIBRARY_PATH=<buildout-directory>/parts/gdal-compile/lib
    #     GISPASS=''

    token = get_auth_token()

    if sys.argv[1] == 'url':

        url = get_feature_url()
        # url = _get_token_service_url(endpoint)
        token = get_auth_token()
        print
        print "Token:", token
        print
        print "Feature URL: ", url + "?token=" + token
        print
        print "Query URL: ", url + "/query?token=" + token
        print

    elif sys.argv[1] == 'dump':
        print "Dumping..."

        if len(sys.argv) > 2:
            path = sys.argv[2]
        else:
            path = 'out.xml'
        res = query_layer(token=token)
        backup_data(res['features'], path=path)

    elif sys.argv[1] == 'summary':
        res = query_layer(token=token)
        print "Summary {0} entries...".format(len(res['features']))

        for entry in res['features']:
            geo = '{0} x {1}'.format(*entry['geometry'].values())
            attr = entry['attributes']
            print attr['FID'], ': ', attr['itemname'], ' @ ', geo

    elif sys.argv[1] == 'del':
        print "Deleting..."
        fid = sys.argv[2]
        res = delete_casestudy(int(fid))
        print res

    elif sys.argv[1] == 'delall':
        print "Deleting all..."
        print delete_all_casestudies(token)

    elif sys.argv[1] == 'addall':
        path = sys.argv[2]
        print add_all_casestudies(path, token)

    elif sys.argv[1] == 'edit':
        print "Editing..."
        fid = sys.argv[2]
        path = sys.argv[3]
        edit_casestudy(fid, path, token)

    elif sys.argv[1] == 'getfid':
        print "Getting FID for measureid..."
        measureid = sys.argv[2]
        print "FID: ", _get_obj_FID(uid=int(measureid))

    else:
        print "Invalid command"


if __name__ == "__main__":
    main()
