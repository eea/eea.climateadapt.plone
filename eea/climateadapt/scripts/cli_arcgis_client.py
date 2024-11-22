""" A command line ArcGIS client

Call it from a script such as:

    #!/bin/bash
    export LD_LIBRARY_PATH=../../../../../parts/gdal-compile/lib
    export GISPASS=mypass
    ../../../../../bin/zopepy sync_to_arcgis.py "$@"

This commands accepts various parameter. Look at __main__ to see what it does.

# TODO: this script is hackish. Maybe optparse would improve feeling.
"""

import argparse
import json
import logging
import os
import sys

from lxml.etree import Element, SubElement, fromstring, tostring

from eea.climateadapt.sat.arcgis import (_get_obj_OBJECTID, apply_edits,
                                         get_auth_token, query_layer)
from eea.climateadapt.sat.settings import get_feature_url

logger = logging.getLogger('eea.climateadapt')
logging.basicConfig()


def backup_data(data, path='out.xml'):
    """ Makes an XML backup data from existing data in ArcGIS
    """
    root = Element("casestudies")

    for cs in data:
        e_cs = SubElement(root, 'casestudy')
        e_attrs = SubElement(e_cs, 'attributes')

        for k, v in list(cs['attributes'].items()):
            el = Element(k)
            el.text = str(v)
            e_attrs.append(el)

        e_geo = SubElement(e_cs, 'geometry')

        for k, v in list(cs.get('geometry', {}).items()):
            el = Element(k)
            el.text = str(v)
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
    all_ids = [x['attributes']['OBJECTID'] for x in res['features']]

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

        for c in e_attrs.iterchildren():
            e['attributes'][c.tag] = (c.text or "").strip()

        e_geo = e_cs.find('geometry')

        for c in e_geo.iterchildren():
            if not c.text:
                logger.error('No value for geo')

                continue
            e['geometry'][c.tag] = float(c.text.strip())

        entries.append(e)

    return entries


def edit_casestudy(fid, path, token):
    """ Used from command line
    """

    entries = parse_dump(path)
    entry = None

    for e in entries:
        if e['attributes']['OBJECTID'] == fid:
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
        entry['geometry']["spatialReference"] = {"wkid": 3857}

        desc = entry['attributes']['desc_']
        try:
            html = fromstring(desc)
            desc = tostring(html, encoding='utf-8', method='text').strip()
        except:
            # probably already plain text
            logger.error("Could not convert %s", desc)

        entry['attributes']['desc_'] = desc

    res = apply_edits(json.dumps(entries), op='adds', token=token)

    return res


def main():
    # Needs env vars:
    #     LD_LIBRARY_PATH=<buildout-directory>/parts/gdal-compile/lib
    #     GISPASS=''

    parser = argparse.ArgumentParser(
        description="Manual operations with ArcGIS"
    )
    parser.add_argument("-u", "--get-feature-url", action="store_true")
    parser.add_argument("-d", "--dump", action="store_true")
    parser.add_argument("-s", "--summary", action="store_true")

    parser.add_argument("-x", "--delete", action="store_true")
    parser.add_argument("-g", "--get-fid", action="store_true")

    parser.add_argument("fid", nargs="?", type=int, default=None)

    parser.add_argument("-X", "--delete-all", action="store_true")

    parser.add_argument("-f", "--import-file", type=str, action="store")
    parser.add_argument("-e", "--edit-file", type=str, action="store")

    args = parser.parse_args()

    passwd = os.environ.get('GISPASS')

    if not passwd:
        logger.error("You need to provide the GISPASS env variable")
        sys.exit(1)

    token = get_auth_token()

    if args.get_feature_url:
        url = get_feature_url()
        # url = _get_token_service_url(endpoint)
        logger.warning(" ")
        logger.warning("Token: %s", token)
        logger.warning(" ")
        logger.warning("Feature URL: %s ?token= %s", url, token)
        logger.warning(" ")
        logger.warning("Query URL: %s/query?token=%s", url,  token)
        logger.warning(" ")
        
    if args.dump:
        logger.warning("Dumping...")

        if len(sys.argv) > 2:
            path = sys.argv[2]
        else:
            path = 'out.xml'
        res = query_layer(token=token)
        backup_data(res['features'], path=path)

    if args.summary:
        res = query_layer(token=token)
        logger.warning("Summary %s entries.... ", len(res['features']))

        for entry in res['features']:
            geo = '{0} x {1}'.format(*list(entry['geometry'].values()))
            attr = entry['attributes']
            logger.warning('%s:%s @ %s', attr['OBJECTID'], attr['itemname'], geo)

    if args.delete:
        logger.warning("Deleting...")
        res = delete_casestudy(args.fid, token)
        logger.warning(res)

    if args.delete_all:
        logger.warning("Deleting all...")
        logger.warning(delete_all_casestudies(token))

    if args.import_file:
        logger.warning(add_all_casestudies(args.import_file, token))

    if args.edit_file:
        logger.warning("Editing...")
        fid = args.fid
        assert fid is not None
        edit_casestudy(fid, args.edit_file, token)

    if args.get_fid:
        logger.warning ("Getting OBJECTID for measureid...")
        measureid = args.fid    # I know, fake
        logger.warning("OBJECTID: %s", _get_obj_OBJECTID(uid=int(measureid)))

    logger.warning("No arguments")


if __name__ == "__main__":
    main()
