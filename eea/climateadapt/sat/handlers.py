""" Handlers for various lifecycle events of CaseStudies
"""

import json
import logging

from eea.climateadapt.sat.arcgis import (_get_obj_OBJECTID, apply_edits,
                                         get_auth_token)
from eea.climateadapt.sat.utils import _get_obj_by_measure_id
from plone.api.content import get_state
from plone.app.iterate.interfaces import IWorkingCopy

logger = logging.getLogger('eea.climateadapt.arcgis')


def handle_ObjectModifiedEvent(site, uid):
    obj = _get_obj_by_measure_id(site, uid)
    repr = obj._repr_for_arcgis()

    token = get_auth_token()

    fid = _get_obj_OBJECTID(obj, token=token)

    if fid is None:
        logger.info("ArcGIS: Adding CaseStudy with measure id %s", uid)
        entry = json.dumps([repr])
        res = apply_edits(entry, op='adds', token=token)
        assert len(res.get('addResults', [])) == 1
        assert res['addResults'][0]['success'] is True
    else:
        repr['attributes']['OBJECTID'] = fid

        logger.info("ArcGIS: Updating CaseStudy with OBJECTID %s", fid)

        entry = json.dumps([repr])
        res = apply_edits(entry, op='updates', token=token)

        assert res['updateResults']
        assert res['updateResults'][0]['objectId'] == fid


def handle_ObjectRemovedEvent(site, uid):
    token = get_auth_token()

    fid = _get_obj_OBJECTID(obj=None, uid=uid, token=token)

    logger.info("ArcGIS: Deleting CaseStudy with OBJECTID %s", fid)

    res = apply_edits(fid, op='deletes', token=token)

    assert res['deleteResults']
    assert res['deleteResults'][0]['objectId'] == fid


def handle_ObjectStateModified(site, uid):
    """ Handle when a CaseStudy is published / unpublished

    If published:
        * if this is a working copy, abort
        * check if object already exists in ArcGIS
            * if doesn't exist, add one
            * if exists, update the existing one
    If unpublished:
        * if this is a working copy, abort
        * check if object exists in ArcGIS
            * if exists, remove it
    """
    obj = _get_obj_by_measure_id(site, uid)

    if IWorkingCopy.providedBy(obj):
        logger.debug("Skipping CaseStudy status change processing")

        return

    state = get_state(obj)

    try:
        token = get_auth_token()
    except KeyError:
        logger.exception("Could not get an Arcgis auth token")

        return

    fid = _get_obj_OBJECTID(obj=obj, token=token)

    if (state != 'published') and fid:
        # it's unpublished, we'll remove the object
        logger.info("ArcGIS: Deleting CaseStudy with OBJECTID %s", fid)

        res = apply_edits(fid, op='deletes', token=token)

        assert res['deleteResults']
        assert res['deleteResults'][0]['objectId'] == fid

        return

    if state == "published":
        repr = obj._repr_for_arcgis()

        # new case study, add it to ArcGIS

        if fid is None:
            logger.info("ArcGIS: Adding CaseStudy with measure id %s", uid)
            entry = json.dumps([repr])
            res = apply_edits(entry, op='adds', token=token)
            assert len(res.get('addResults', [])) == 1
            assert res['addResults'][0]['success'] is True

        # existing case study, sync its info
        else:
            logger.info("ArcGIS: Updating CaseStudy with OBJECTID %s", fid)

            repr['attributes']['OBJECTID'] = fid
            entry = json.dumps([repr])
            res = apply_edits(entry, op='updates', token=token)

            assert res['updateResults']
            assert res['updateResults'][0]['objectId'] == fid


HANDLERS = {
    'ObjectModifiedEvent': handle_ObjectModifiedEvent,
    'ObjectRemovedEvent': handle_ObjectRemovedEvent,
    'ActionSucceededEvent': handle_ObjectStateModified,
}
