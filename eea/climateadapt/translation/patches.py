import logging

from Acquisition import aq_self
from BTrees.OIBTree import OIBTree
from plone.api import portal
from plone.app.multilingual.dx.interfaces import (IDexterityTranslatable,
                                                  ILanguageIndependentField)
from plone.app.multilingual.factory import DefaultTranslationLocator as Base
from plone.app.multilingual.interfaces import (
    ILanguage, ILanguageIndependentFieldsManager, ITranslationLocator,
    ITranslationManager)
from plone.dexterity.utils import iterSchemata
from z3c.relationfield.interfaces import IRelationList, IRelationValue
from zope.annotation.interfaces import IAnnotations
from zope.component import queryAdapter  # getUtility,
from zope.component import ComponentLookupError
from zope.interface import implementer

from eea.climateadapt.asynctasks.utils import get_async_service

from .core import (DummyPersistent, sync_language_independent_fields,
                   wrap_in_aquisition)

logger = logging.getLogger("eea.climateadapt")


_marker = object()


def path(obj):
    return "/".join(obj.getPhysicalPath())


@implementer(ITranslationLocator)
class DefaultTranslationLocator(Base):
    def __call__(self, language):
        """
        Look for the closest translated folder or siteroot
        """
        parent = super(DefaultTranslationLocator, self).__call__(language)
        path = "/".join(parent.getPhysicalPath())
        site = portal.get()
        parent = wrap_in_aquisition(path, site)
        return parent


def copy_fields_patched(self, translation):
    # import pdb
    #
    # pdb.set_trace()
    print(("patched copy fields", translation))
    # copy and adapted from https://github.com/plone/plone.app.multilingual/blob/9e7491294f01f7bd21a45e00231d54873ad0eed6/src/plone/app/multilingual/dx/cloner.py
    changed = False

    adapter = queryAdapter(translation, ILanguage)
    if adapter is None:
        logger.exception(
            "Didn't find language for translation: %s", translation)
        return
    target_language = adapter.get_language()

    for schema in iterSchemata(self.context):
        context_adapter = None
        translation_adapter = None
        for field_name in schema:
            if ILanguageIndependentField.providedBy(schema[field_name]):
                if context_adapter is None:
                    context_adapter = schema(self.context)
                value = getattr(context_adapter, field_name, _marker)
                field_changed = None
                if value == _marker:
                    continue
                elif IRelationValue.providedBy(value):
                    field_changed = True
                    value = self.copy_relation(value, target_language)
                elif IRelationList.providedBy(schema[field_name]):
                    field_changed = True
                    if not value:
                        value = []
                    else:
                        new_value = []
                        for relation in value:
                            copied_relation = self.copy_relation(
                                relation, target_language
                            )
                            if copied_relation:
                                new_value.append(copied_relation)
                        value = new_value

                if translation_adapter is None:
                    translation_adapter = schema(translation)

                # We only want to store a new value if it has changed.
                # In general we can compare equality of the new value to the one on the translation.
                # But RelationValue.__eq__ is broken if the relation doesn't have a from_object,
                # so for now we force field_changed to True for relations above.
                if field_changed is None:
                    translation_value = getattr(
                        translation_adapter, field_name, _marker
                    )
                    field_changed = value != translation_value
                if field_changed:
                    changed = True
                    setattr(translation_adapter, field_name, value)

    # If at least one field has been copied over to the translation
    # we need to inform subscriber to trigger an ObjectModifiedEvent
    # on that translation.
    return changed


def handle_modified_patched(self, content):
    # import pdb; pdb.set_trace()
    fieldmanager = ILanguageIndependentFieldsManager(content)
    if not fieldmanager.has_independent_fields():
        return

    en_obj_path = "/".join(content.getPhysicalPath())
    if "cca/en" not in en_obj_path:
        return

    http_host = content.REQUEST.environ.get(
        "HTTP_X_FORWARDED_HOST", portal.get().absolute_url()
    )
    options = {"http_host": http_host}

    logger.info("Queing job to copy language independent fields %s", en_obj_path)
    try:
        async_service = get_async_service()
        queue = async_service.getQueues()[""]
        async_service.queueJobInQueue(
            queue,
            ("translate",),
            sync_language_independent_fields,
            DummyPersistent(),
            en_obj_path,
            options,
        )
    except ComponentLookupError:
        logger.error(
            "Unable to queue job to copy language independent fields %s", en_obj_path
        )

    # return self._old_handle_modified(content)


def patched_default_order_init(self, context):
    """Delegate ordering to the canonical version of an object"""
    self._is_translation = False

    if IDexterityTranslatable.providedBy(context):
        aq_context = aq_self(context)
        lang = getattr(aq_context, "language", None)

        if lang and lang != "en":
            canonical = ITranslationManager(context).get_translation("en")
            if canonical:
                self._is_translation = True
                self.context = canonical
                self.translation = context
                import logging

                logger = logging.getLogger("eea.climateadapt")
                logger.info(
                    "Using canonical %s for %s",
                    path(canonical),
                    path(context),
                )
                return
            else:
                import logging

                logger = logging.getLogger("eea.climateadapt")
                logger.info("Could not find canonical for %s", path(context))

    self.context = context


def patched_default_order_pos(self, create=False):
    annotations = IAnnotations(self.context)

    if self._is_translation:
        try:
            tree = self.translation._tree
            ids = list(tree.keys())
            pos = annotations.get(self.POS_KEY, {})
            res = {}
            for k in list(pos.keys()):
                if k in ids:
                    res[k] = pos[k]
            return res
        except Exception:
            logger.exception(
                "Could not properly get order %s", path(self.translation)
            )
    else:
        if create:
            return annotations.setdefault(self.POS_KEY, OIBTree())
        return annotations.get(self.POS_KEY, {})


def patched_default_order_order(self, create=False):
    annotations = IAnnotations(self.context)

    if self._is_translation:
        try:
            tree = self.translation._tree
            ids = list(tree.keys())
            pos = annotations.get(self.ORDER_KEY, [])
            res = [k for k in pos if k in ids]
            return res
        except Exception:
            logger.exception(
                "Could not properly get order %s", path(self.translation)
            )
    else:
        if create:
            return annotations.setdefault(self.POS_KEY, OIBTree())
        return annotations.get(self.POS_KEY, {})


def patched_default_getObjectPosition(self, obj_id):
    """see interfaces.py"""
    pos = self._pos()
    if obj_id in pos:
        return pos[obj_id]

    # TODO: lookup the position for the translation of that object
    logger.warning(
        "Could not find position of %s in %s", obj_id, path(self.context)
    )
    return 0

    # raise ValueError(
    #     'No object with id "{:s}" exists in "{:s}".'.format(
    #         obj_id, "/".join(self.context.getPhysicalPath())
    #     )
    # )


# fix the translation locator to allow it to properly work in async
# from plone.app.multilingual.interfaces import ILanguageIndependentFieldsManager
# from plone.app.multilingual.dx.cloner import LanguageIndependentFieldsManager
# from plone.base.interfaces import ILanguage
# from plone.base.utils import safe_text
# ITranslationManager,
# from zope.intid.interfaces import IIntIds
# from z3c.relationfield import RelationValue


# def copy_relation_patched(self, relation_value, target_language):
#     if not relation_value or relation_value.isBroken():
#         return
#
#     obj = relation_value.to_object
#     intids = getUtility(IIntIds)
#     translation = ITranslationManager(obj).get_translation(target_language)
#     if translation:
#         return RelationValue(intids.getId(translation))
#     return RelationValue(intids.getId(obj))
