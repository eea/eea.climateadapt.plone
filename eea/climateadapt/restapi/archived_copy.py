# -*- coding: utf-8 -*-
from plone import api
from plone.api.exc import InvalidParameterError
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import getMultiAdapter

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

        # Update relatedItems bidirectionally using plone.api.relation
        # The copied object inherits the source's relatedItems; clear them first.
        api.relation.delete(source=archived, relationship="relatedItems")

        # Archived copy points back to the original (latest) indicator
        api.relation.create(
            source=archived, target=context, relationship="relatedItems"
        )

        # Original indicator gets a link to the archived copy
        api.relation.create(
            source=context, target=archived, relationship="relatedItems"
        )

        # Reindex
        archived.reindexObject()
        context.reindexObject()

        # Serialize and return
        serializer = getMultiAdapter((archived, self.request), ISerializeToJson)
        return serializer()
