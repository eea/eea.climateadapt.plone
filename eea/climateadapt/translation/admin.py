import json
import logging
from urllib.parse import parse_qs, urlparse

from BTrees.OIBTree import OIBTree
from persistent.list import PersistentList
from plone import schema
from plone.api import content, portal
from plone.app.multilingual.dx.interfaces import IDexterityTranslatable
from plone.app.multilingual.interfaces import ITG, ITranslationManager
from plone.app.multilingual.itg import ATTRIBUTE_NAME
from plone.autoform.form import AutoExtensibleForm
from plone.base.utils import base_hasattr
from plone.dexterity.interfaces import IDexterityContainer
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button, form
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface, alsoProvides

from eea.climateadapt.translation.core import find_untranslated, queue_translate
from eea.climateadapt.utils import force_unlock

from .core import ingest_html, queue_job, setup_translation_object
from .utils import get_site_languages

logger = logging.getLogger("eea.climateadapt.translation")


class IIngestForm(Interface):
    text = schema.Text(
        title="HTML",
    )


class HTMLIngestion(AutoExtensibleForm, form.Form):
    schema = IIngestForm
    ignoreContext = True

    label = "Ingest JSON"
    description = "Object with keys jobData, copied from bull dashboard"

    def extractData(self, setErrors=True):
        data, errors = super().extractData(setErrors)
        jobData = json.loads(data["text"])["jobData"]
        return jobData, errors

    def applyChanges(self, data):
        html = data["html"]
        path = data["obj_path"]

        url = f"https://climateadapt.com/{path}"
        parsed_url = urlparse(url)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        language = query_params["language"][0]

        if not (html and path):
            return self.index()

        site_portal = portal.getSite()

        en_obj = site_portal.unrestrictedTraverse(path)

        trans_obj = setup_translation_object(en_obj, language, self.request)

        ingest_html(trans_obj, html)
        return {"ok": True}

    @button.buttonAndHandler("Ok")
    def handleApply(self, action):
        data, errors = self.extractData()
        # import pdb
        #
        # pdb.set_trace()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.applyChanges(data)
        self.status = "Saved"

    @button.buttonAndHandler("Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page."""


# class HTMLIngestion(BrowserView):
#     """A special view to allow manually submit an HTML translated by
#     eTranslation, but that wasn't properly submitted through the callback"""
#
#     def __call__(self):
#         alsoProvides(self.request, IDisableCSRFProtection)
#         # self.request.environ["HTTP_X_THEME_DISABLED"] = "1"
#
#         html = self.request.form.get("html", "")
#         path = self.request.form.get("path", "")
#
#         if not (html and path):
#             return self.index()
#
#         site = portal.getSite()
#         trans_obj = site.unrestrictedTraverse(path)
#         ingest_html(trans_obj, html)
#         return "ok"


class TranslateObjectAsync(BrowserView):
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        messages = IStatusMessage(self.request)
        messages.add("Translation process initiated.", type="info")

        obj_url = self.context.absolute_url()
        language = self.request.form.get("lang", None) or self.request.form.get(
            "language", None
        )

        queue_translate(self.context, language)

        return self.request.response.redirect(obj_url)


class TranslateMissing(BrowserView):
    """A view to trigger the translation for missing translations"""

    blacklist = [
        "Image",
        "File",
        "LRF",
        "LIF",
        "Subsite",
        "FrontpageSlide",
    ]

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        context = self.context

        brains = context.portal_catalog.searchResults(
            path="/".join(context.getPhysicalPath()),
            sort="path",
            review_state="published",
        )

        for i, brain in enumerate(brains):
            obj = brain.getObject()
            if brain.portal_type in self.blacklist:
                continue
            if "sandbox" in obj.absolute_url():
                continue

            if "lang" in self.request.form:
                langs = find_untranslated(obj, [self.request.form["lang"]])
            else:
                langs = find_untranslated(obj, get_site_languages())

            force_unlock(obj)
            url = obj.absolute_url()

            for language in langs:
                logger.info("Queuing %s for translation for %s", url, language)

                queue_translate(obj, language)

        return "ok"


class TranslateFolderAsync(BrowserView):
    """Exposed in /see_folder_objects"""

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        context = self.context

        brains = context.portal_catalog.searchResults(
            path="/".join(context.getPhysicalPath()),
            sort="path",
        )
        lang = self.request.form.get("language", None)

        for i, brain in enumerate(brains):
            obj = brain.getObject()
            if "sandbox" in obj.absolute_url():
                continue

            if lang is None:
                langs = find_untranslated(obj, get_site_languages())
            else:
                langs = [lang]

            force_unlock(obj)
            for language in langs:
                url = obj.absolute_url()
                logger.info("Queuing %s for translation for %s", url, language)

                queue_translate(obj, language)

            # if i % 20 == 0:
            #     transaction.commit()

        messages = IStatusMessage(self.request)
        messages.add("Translation process initiated.", type="info")

        return self.request.response.redirect(self.context.absolute_url())


class FixFolderOrder(BrowserView):
    ORDER_KEY = "plone.folder.ordered.order"
    POS_KEY = "plone.folder.ordered.pos"

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        path = "/".join(self.context.getPhysicalPath())
        brains = self.context.portal_catalog.searchResults(sort_on="path", path=path)

        for brain in brains:
            obj = brain.getObject()
            base_path = obj.getPhysicalPath()
            if not IDexterityTranslatable.providedBy(obj):
                continue

            if not IDexterityContainer.providedBy(obj):
                continue

            language = obj.language

            if language is None:
                logger.warning(
                    "Language is set to None for %s", "/".join(obj.getPhysicalPath())
                )
                continue

            canonical = ITranslationManager(obj).get_translation("en")

            if canonical:
                annotations = IAnnotations(canonical)
                trans_annot = IAnnotations(obj)

                annotations = IAnnotations(canonical)
                trans_annot = IAnnotations(obj)

                self.fix_order(
                    obj, canonical, annotations, trans_annot, language, base_path
                )
                self.fix_pos(
                    obj, canonical, annotations, trans_annot, language, base_path
                )

        return "done"

    def fix_order(self, obj, canonical, annotations, trans_annot, language, base_path):
        tree = obj._tree
        obj_ids = list(tree.keys())

        # order is a list like: ['index_html', 'organisations', 'international']
        proper_order = list(annotations.get(self.ORDER_KEY, []))
        orig_order = list(trans_annot.get(self.ORDER_KEY, []))

        if proper_order != orig_order:
            trans_order = PersistentList()
            # rebuild the order
            orig_order_set = set(orig_order)
            for id in proper_order:
                if id in obj_ids:
                    trans_order.append(id)
                    if id in orig_order_set:
                        orig_order_set.remove(id)
                else:
                    # was the object translated with another id?
                    other = canonical._getOb(id)
                    try:
                        trans = ITranslationManager(other).get_translation(language)
                    except TypeError:
                        logger.warning(
                            "Object not translatable: %s",
                            "/".join(other.getPhysicalPath()),
                        )
                        continue
                    if trans:
                        test_path = trans.getPhysicalPath()[:-1]

                        if test_path == base_path:
                            new_id = trans.getId()
                            if new_id in orig_order_set:
                                orig_order_set.remove(new_id)
                            trans_order.append(new_id)
                        else:
                            logger.warning(
                                "Translated object is in another folder: %s (should be: %s )",
                                base_path,
                                "/".join(trans.getPhysicalPath()),
                            )
                    else:
                        logger.info(
                            "Original without translation: %s (%s)",
                            "/".join(other.getPhysicalPath()),
                            language,
                        )

            for key in (
                orig_order_set
            ):  # append remaining keys that were not found in canonical
                trans_order.append(key)

            if trans_order:
                trans_annot[self.ORDER_KEY] = trans_order
                logger.info(
                    "Fixed order for %s. Old: %r. New: %r",
                    "/".join(obj.getPhysicalPath()),
                    orig_order,
                    list(trans_order),
                )

    def fix_pos(self, obj, canonical, annotations, trans_annot, language, base_path):
        tree = obj._tree
        obj_ids = list(tree.keys())

        # pos is a mapping like: {'index_html': 0, 'international': 2, 'organisations': 1}
        proper_pos = dict(annotations.get(self.POS_KEY, {}))
        orig_pos = dict(trans_annot.get(self.POS_KEY, {}))

        if proper_pos != orig_pos:
            trans_pos = OIBTree()
            # rebuild the order
            orig_order_set = set(orig_pos.keys())
            for id, position in list(proper_pos.items()):
                if id in obj_ids:
                    trans_pos[id] = position
                    if id in orig_order_set:
                        orig_order_set.remove(id)
                else:
                    # was the object translated with another id?
                    other = canonical._getOb(id)
                    try:
                        trans = ITranslationManager(other).get_translation(language)
                    except TypeError:
                        logger.warning(
                            "Object not translatable: %s",
                            "/".join(other.getPhysicalPath()),
                        )
                        continue
                    if trans:
                        test_path = trans.getPhysicalPath()[:-1]

                        if test_path == base_path:
                            new_id = trans.getId()
                            if new_id in orig_order_set:
                                orig_order_set.remove(new_id)
                            trans_pos[new_id] = position
                        else:
                            logger.warning(
                                "Translated object is in another folder: %s (should be: %s )",
                                base_path,
                                "/".join(trans.getPhysicalPath()),
                            )
                    else:
                        logger.info(
                            "Original without translation: %s (%s)",
                            "/".join(other.getPhysicalPath()),
                            language,
                        )

            # TODO: add missing pos from original
            for k in orig_order_set:
                if k not in trans_pos:
                    trans_pos[k] = orig_pos[k]
            if trans_pos:
                trans_annot[self.POS_KEY] = trans_pos
                logger.info(
                    "Fixed position for %s. Old: %r. New: %r",
                    "/".join(obj.getPhysicalPath()),
                    orig_pos,
                    dict(trans_pos),
                )


class SeeTranslationStatus(BrowserView):
    blacklist = [
        "Image",
        "File",
        "LRF",
        "LIF",
        "Subsite",
        "FrontpageSlide",
    ]

    def good_lang_codes(self):
        return get_site_languages()

    def find_untranslated(self, obj):
        tm = ITranslationManager(obj)
        translations = tm.get_translations()
        untranslated = set(get_site_languages())

        for langcode, obj in translations.items():
            if langcode == "en":
                continue
            if obj.title and langcode in untranslated:
                untranslated.remove(langcode)

        return list(untranslated)

    def brains(self):
        context = self.context

        brains = context.portal_catalog.searchResults(
            path="/".join(context.getPhysicalPath()),
            sort="path",
            # review_state="published",
        )

        result = []

        for i, brain in enumerate(brains):
            if brain.portal_type in self.blacklist:
                continue
            obj = brain.getObject()
            langs = self.find_untranslated(obj)
            result.append((brain, langs))

        return result


class SyncTranslationPaths(BrowserView):
    def check_translation_paths(self, obj):
        try:
            tm = ITranslationManager(obj)
            translations = tm.get_translations()
        except Exception:
            return []

        bits = obj.getPhysicalPath()
        if "sandbox" in bits:
            return []

        path = "/".join(bits)
        out = []

        for langcode, trans in translations.items():
            if langcode == "en":
                continue

            if path.replace("/en/", f"/{langcode}/") != "/".join(
                trans.getPhysicalPath()
            ):
                out.append(langcode)

        return out

    def __call__(self):
        context = self.context
        brains = context.portal_catalog.searchResults(
            path="/".join(context.getPhysicalPath()),
            sort="path",
            # review_state="published",
        )

        for brain in brains:
            if brain.portal_type == "LRF":
                continue

            obj = brain.getObject()
            broken_langs = self.check_translation_paths(obj)

            parent_path = "/".join(obj.aq_parent.getPhysicalPath())

            for lang in broken_langs:
                data = {
                    "newName": obj.getId(),
                    "oldName": obj.getId(),
                    "oldParent": parent_path,
                    "newParent": parent_path,
                    "langs": [lang],
                }
                opts = {
                    "delay": 10000,
                    "priority": 1,
                    "attempts": 3,
                    "lifo": False,
                }
                queue_job("sync_paths", "sync_translated_paths", data, opts)


class CleanupFolderOrder(BrowserView):
    ORDER_KEY = "plone.folder.ordered.order"
    POS_KEY = "plone.folder.ordered.pos"

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        context = self.context
        has = base_hasattr

        def fixObject(obj, path):
            if has(obj, "_tree") and has(obj, "__annotations__"):
                folder_keys = tuple(obj._tree.keys())
                order = obj.__annotations__.get(self.ORDER_KEY)

                if order:
                    logger.debug(f"Processing {path}")

                    fixed_order = []
                    for k in order:
                        if (k in folder_keys) and (k not in fixed_order):
                            fixed_order.append(k)
                    for k in folder_keys:
                        if k not in fixed_order:
                            fixed_order.append(k)
                    fixed_order = tuple(fixed_order)

                    if fixed_order != tuple(order):
                        obj_path = "/".join(obj.getPhysicalPath())
                        logger.info(f"Fixing position for {obj_path}")
                        obj.__annotations__[self.ORDER_KEY] = PersistentList(
                            fixed_order
                        )
                        trans_pos = OIBTree()
                        for i, k in enumerate(fixed_order):
                            trans_pos[k] = i
                        obj.__annotations__[self.POS_KEY] = trans_pos
                        obj.__annotations__._p_changed = True

        fixObject(context, "")
        site = portal.get()
        site.ZopeFindAndApply(context, search_sub=True, apply_func=fixObject)

        return "done"


def remove_rid(rid, catalog):
    """Nukes a rid (-112343454) from catalog"""

    _catalog = catalog._catalog

    logger.info(f"Removing metadata for {rid}")
    for uid, value in _catalog.uids.items():
        if value == rid:
            del _catalog.uids[uid]
    if rid in _catalog.data:
        del _catalog.data[rid]

    for iname, index in _catalog.indexes.items():
        logger.info(f"Removing from {iname}")
        index.unindex_object(rid)


class RemoveUnmatchedTranslations(BrowserView):
    """Find the equivalent path of translations. If they're not in the same translation group, delete them"""

    def fixObject(self, obj, path, force_delete=False):
        # logger.debug(f"Looking at {path}")
        obj_path_bits = list(obj.getPhysicalPath())
        obj_path = "/".join(obj_path_bits)

        try:
            trans_tg = str(ITG(obj))
        except TypeError:
            logger.warning(f"Not in a tg {obj_path}")
            return

        en_path = obj_path_bits[:]
        en_path[2] = "en"
        en_obj_path = "/".join(en_path)
        en_obj = content.get(en_obj_path)

        if en_obj is None:
            logger.warning(f"EN obj not found on this path: {'/'.join(en_path)}")

            if force_delete:
                delattr(obj, ATTRIBUTE_NAME)
                content.delete(obj=obj, check_linkintegrity=False)
            return

        en_obj_path = "/".join(en_obj.getPhysicalPath())

        try:
            en_tg = str(ITG(en_obj))
        except TypeError:
            logger.warning(f"Something strange with this: {en_obj_path}")
            return

        if trans_tg != en_tg:
            logger.warning(f"Unmatched translation path {obj_path}")
            if force_delete:
                try:
                    delattr(obj, ATTRIBUTE_NAME)
                    content.delete(obj=obj, check_linkintegrity=False)
                except Exception as e:
                    logger.warning(f"Could not delete: {e}")

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        self.request.translation_info = {"tg": "notg"}
        force_delete = bool(self.request.form.get("delete"))

        context = self.context
        catalog = context.portal_catalog

        brains = catalog.unrestrictedSearchResults(
            path="/".join(context.getPhysicalPath()),
            sort="path",
            # review_state="published",
        )
        for i, rid in enumerate(brains._seq):
            try:
                brain = brains._func(rid)
            except Exception as e:
                logger.warning(f"Could not retrieve brain {rid}: {e}")
                remove_rid(rid, catalog)
                continue
            try:
                obj = brain.getObject()
                path = "/".join(obj.getPhysicalPath())
                self.fixObject(obj, path, force_delete)
            except Exception as e:
                logger.warning(f"Could not process {e} ")
                continue

        logger.info("Done")
        return "done"


class SiteRemoveUnmatchedTranslations(RemoveUnmatchedTranslations):
    def fix_language(self, context, force_delete):
        catalog = context.portal_catalog
        brains = catalog.unrestrictedSearchResults(
            path="/".join(context.getPhysicalPath()),
            sort="path",
            # review_state="published",
        )
        for i, rid in enumerate(brains._seq):
            try:
                brain = brains._func(rid)
            except Exception as e:
                logger.warning(f"Could not retrieve brain {rid}: {e}")
                remove_rid(rid, catalog)
                continue
            try:
                obj = brain.getObject()
                path = "/".join(obj.getPhysicalPath())
                self.fixObject(obj, path, force_delete)
            except Exception as e:
                logger.warning(f"Could not process {e} ")
                continue

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        self.request.translation_info = {"tg": "notg"}
        force_delete = bool(self.request.form.get("delete"))

        site = portal.get()
        for lang in get_site_languages():
            if lang == "en":
                continue
            context = site[lang]
            self.fix_language(context, force_delete)

        logger.info("Done")
        return "done"


class FixCatalog(BrowserView):
    def resolve_url(self, path):
        path = path.replace("//cca/", "/cca/")
        try:
            obj = self.context.unrestrictedTraverse(path)
            pp = "/".join(obj.getPhysicalPath())
            assert pp == path
            # print(pp)
            return obj
        except Exception:
            print(f"Resolving failed for {path}")
            return None

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        catalog = self.context.portal_catalog
        self._catalog = catalog._catalog

        paths = self._catalog.paths
        uids = self._catalog.uids
        unchanged = 0
        fixed = []
        removed = []

        for path, rid in uids.items():
            ob = None
            # if path[:1] == "/":
            #     ob = self.resolve_url(path[1:])
            ob = self.resolve_url(path)
            if ob is None:
                removed.append(path)
                continue
            ppath = "/".join(ob.getPhysicalPath())
            if path != ppath:
                fixed.append((path, ppath))
            else:
                unchanged = unchanged + 1

        for path, ppath in fixed:
            rid = uids[path]
            del uids[path]
            paths[rid] = ppath
            uids[ppath] = rid

        logger.info(f"To be removed: {len(removed)}")

        for path in removed:
            logger.info(f"Removing path {path}")
            catalog.uncatalog_object(path)
            break

        return "Done"


class RemoveRid(BrowserView):
    # def cleanup_path_index(self, index, rid):
    #     for k, v in index._index.items():
    #         if v == rid:
    #             del index._index[k]
    #
    #     if rid in index._unindex:
    #         del index._unindex[rid]
    #
    #     for k, v in index._index_parents.items():
    #         if v == rid:
    #             del index._index[k]
    #
    #     for k, v in index._index_items.items():
    #         if v == rid:
    #             del index._index[k]

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        rid = int(self.request.form.get("rid"))
        catalog = self.context.portal_catalog
        remove_rid(rid, catalog)

        logger.info("Done")
        return "Done"


class DeleteTranslationField(BrowserView):
    def fixObject(self, obj, fields):
        path = "/".join(obj.getPhysicalPath())
        assert obj.language != "en"
        has = base_hasattr

        dirty = False
        for fieldname in fields:
            if has(obj, fieldname):
                logger.info(f"Removing {fieldname} from {path}")
                delattr(obj, fieldname)
                dirty = True

        if dirty:
            self.catalog.reindexObject(obj)

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        field = self.request.form.get("field", "image")
        if field:
            fields = [field]
        else:
            fields = [
                "image",
                "logo",
                "primary_photo",
                "promotional_image",
                "preview_image",
            ]
        catalog = self.catalog = self.context.portal_catalog
        brains = catalog.unrestrictedSearchResults(
            path="/".join(self.context.getPhysicalPath()),
            sort="path",
            # review_state="published",
        )
        for i, rid in enumerate(brains._seq):
            try:
                brain = brains._func(rid)
            except Exception as e:
                logger.warning(f"Could not retrieve brain {rid}: {e}")
                remove_rid(rid, catalog)
                continue
            try:
                obj = brain.getObject()
                self.fixObject(obj, fields)
            except Exception as e:
                logger.warning(f"Could not process {e} ")
                continue
