# -*- coding: utf-8 -*-
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.relationfield.behavior import IRelatedItems
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.interface import alsoProvides

import json


class CreateArchivedCopy(Service):
    """Create an archived copy of an indicator."""

    def reply(self):
        data = json.loads(self.request.get("BODY") or "{}")
        title = data.get("title", "").strip()
        new_id = data.get("id", "").strip()

        context = self.context
        container = context.aq_parent

        # Validation: content type
        if context.portal_type != "eea.climateadapt.indicator":
            self.request.response.setStatus(400)
            return {
                "type": "BadRequest",
                "message": "This action is only available for Indicator content types.",
            }

        # Validation: new ID
        if not new_id:
            self.request.response.setStatus(400)
            return {
                "type": "BadRequest",
                "message": "ID is required.",
            }

        if new_id == context.getId():
            self.request.response.setStatus(400)
            return {
                "type": "BadRequest",
                "message": "The archived copy ID must be different from the original indicator ID.",
            }

        if new_id in container.objectIds():
            self.request.response.setStatus(400)
            return {
                "type": "BadRequest",
                "message": f"An object with ID '{new_id}' already exists in this folder.",
            }

        # Validation: permission
        if not api.user.has_permission("Add portal content", obj=container):
            self.request.response.setStatus(403)
            return {
                "type": "Forbidden",
                "message": "You do not have permission to add content here.",
            }

        # Create a copy
        try:
            archived = api.content.copy(source=context, target=container, id=new_id)
        except InvalidParameterError as e:
            self.request.response.setStatus(400)
            return {
                "type": "BadRequest",
                "message": str(e),
            }

        # Update title
        archived.title = title or context.title

        # Apply archive workflow transition
        try:
            api.content.transition(obj=archived, transition="archive")
        except api.exc.InvalidParameterError:
            # Transition may not be available, try setting state directly
            try:
                api.content.transition(obj=archived, transition="publish")
                api.content.transition(obj=archived, transition="archive")
            except Exception:
                pass

        # Update relatedItems bidirectionally
        intids = getUtility(IIntIds)
        source_intid = intids.queryId(context)
        archived_intid = intids.queryId(archived)

        if source_intid and archived_intid:
            # Set relatedItems on archived copy -> points to source
            if IRelatedItems.providedBy(archived):
                archived.relatedItems = [RelationValue(source_intid)]
            else:
                alsoProvides(archived, IRelatedItems)
                archived.relatedItems = [RelationValue(source_intid)]

            # Append archived copy to source's relatedItems
            if IRelatedItems.providedBy(context):
                existing = list(context.relatedItems or [])
                # Avoid duplicates
                existing_ids = {intids.queryId(rel.to_object) for rel in existing if rel.to_object}
                if archived_intid not in existing_ids:
                    existing.append(RelationValue(archived_intid))
                context.relatedItems = existing
            else:
                alsoProvides(context, IRelatedItems)
                context.relatedItems = [RelationValue(archived_intid)]

        # Reindex
        archived.reindexObject()
        context.reindexObject()

        # Serialize and return
        serializer = ISerializeToJson(archived, self.request)
        return serializer()
