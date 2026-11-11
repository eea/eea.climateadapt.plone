"""Regression tests for the translation path-sync deletion guard.

Moving an English object used to delete whatever translation already lived at
the destination path, unconditionally and silently. When that occupant was the
translation of a *different* live English object - or a folder with a subtree
under it - unrelated translated content was destroyed. The eu-adaptation
regression of 2026-11-10 (289 objects lost Turkish) came from exactly this.

The fix identifies the occupant's canonical owner, logs the deletion, and puts
that owner back in the translation queue. These tests cover that decision
logic without needing a full Plone site.
"""

import unittest
from unittest import mock

from eea.climateadapt.translation import core


class FakeObject:
    """Minimal stand-in for a content object."""

    def __init__(self, uid, path, portal_type="Document", children=None):
        self.uid = uid
        self._path = path
        self.portal_type = portal_type
        self._children = children or []

    def getPhysicalPath(self):
        return tuple(self._path.split("/"))

    def objectIds(self):
        return list(self._children)

    def __repr__(self):  # pragma: no cover - debugging aid
        return f"<FakeObject {self._path}>"


class FakeTranslationManager:
    def __init__(self, translations):
        self._translations = translations

    def get_translations(self):
        return self._translations


def _tm_for(mapping):
    """Return an ITranslationManager replacement keyed by object uid."""

    def side_effect(obj):
        translations = mapping.get(getattr(obj, "uid", None))
        if translations is None:
            raise TypeError("object is not translatable")
        return FakeTranslationManager(translations)

    return side_effect


class TestTranslationOwner(unittest.TestCase):
    """_translation_owner must identify who a translation belongs to."""

    def test_returns_canonical_for_a_translation(self):
        en = FakeObject("en-1", "/cca/en/eu-adaptation")
        tr = FakeObject("tr-1", "/cca/tr/eu-adaptation")
        with mock.patch.object(
            core, "ITranslationManager", _tm_for({"tr-1": {"en": en, "tr": tr}})
        ):
            self.assertIs(core._translation_owner(tr), en)

    def test_returns_none_for_the_canonical_object_itself(self):
        en = FakeObject("en-1", "/cca/en/eu-adaptation")
        tr = FakeObject("tr-1", "/cca/tr/eu-adaptation")
        with mock.patch.object(
            core, "ITranslationManager", _tm_for({"en-1": {"en": en, "tr": tr}})
        ):
            self.assertIsNone(core._translation_owner(en))

    def test_returns_none_for_an_orphan_with_no_english_member(self):
        tr = FakeObject("tr-1", "/cca/tr/gone")
        with mock.patch.object(
            core, "ITranslationManager", _tm_for({"tr-1": {"tr": tr}})
        ):
            self.assertIsNone(core._translation_owner(tr))

    def test_returns_none_for_non_translatable_types(self):
        # Image/File and friends raise TypeError from ITranslationManager.
        img = FakeObject("img-1", "/cca/en/photo.png", portal_type="Image")
        with mock.patch.object(core, "ITranslationManager", _tm_for({})):
            self.assertIsNone(core._translation_owner(img))

    def test_returns_none_when_the_group_cannot_be_read(self):
        tr = FakeObject("tr-1", "/cca/tr/broken")

        def boom(obj):
            return mock.Mock(get_translations=mock.Mock(side_effect=RuntimeError))

        with mock.patch.object(core, "ITranslationManager", boom):
            self.assertIsNone(core._translation_owner(tr))


class TestRequeueSubtree(unittest.TestCase):
    """Deleting a translated folder must re-queue its whole subtree."""

    def _catalog(self, objs):
        brains = []
        for o in objs:
            brain = mock.Mock()
            brain.getObject.return_value = o
            brains.append(brain)
        catalog = mock.Mock()
        catalog.searchResults.return_value = brains
        return catalog

    def test_queues_every_translatable_object_in_the_subtree(self):
        en = FakeObject("en-1", "/cca/en/section", children=["a"])
        child = FakeObject("en-2", "/cca/en/section/a")
        mapping = {"en-1": {"en": en}, "en-2": {"en": child}}

        with mock.patch.object(core, "getToolByName", return_value=self._catalog([en, child])), \
             mock.patch.object(core, "ITranslationManager", _tm_for(mapping)), \
             mock.patch.object(core, "queue_translate") as queued:
            core._requeue_subtree_for_translation(en, "tr")

        self.assertEqual(queued.call_count, 2)
        langs = [c.args[1] for c in queued.call_args_list]
        self.assertEqual(langs, ["tr", "tr"])

    def test_skips_non_translatable_objects_in_the_subtree(self):
        en = FakeObject("en-1", "/cca/en/section")
        img = FakeObject("img-1", "/cca/en/section/photo.png", portal_type="Image")

        with mock.patch.object(core, "getToolByName", return_value=self._catalog([en, img])), \
             mock.patch.object(core, "ITranslationManager", _tm_for({"en-1": {"en": en}})), \
             mock.patch.object(core, "queue_translate") as queued:
            core._requeue_subtree_for_translation(en, "tr")

        self.assertEqual(queued.call_count, 1)
        self.assertIs(queued.call_args_list[0].args[0], en)


if __name__ == "__main__":
    unittest.main()
