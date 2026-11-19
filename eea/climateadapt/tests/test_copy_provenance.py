# -*- coding: utf-8 -*-
"""Tests for Taskman #309870 - creator/dates of duplicated content.

Duplicating content in Climate-ADAPT goes through ``OFS.CopySupport``, which
deep-copies the original object. Everything below pins down what a copy is
allowed to inherit from its source.
"""

import transaction
import unittest
from datetime import timedelta
from unittest import mock

from DateTime import DateTime
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from eea.climateadapt import events
from eea.climateadapt.testing import EEA_CLIMATEADAPT_INTEGRATION_TESTING


class FakeMember:
    """Stand-in for the member that plone.api.user.get_current() returns."""

    def __init__(self, user_id):
        self.user_id = user_id

    def getId(self):
        return self.user_id


class TestObjectCopiedEvent(unittest.TestCase):
    layer = EEA_CLIMATEADAPT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.portal.invokeFactory("Document", "original", title="Original")
        self.original = self.portal["original"]
        self.original.creators = ("costasil",)
        self.original.contributors = ("someoneelse",)
        self.original.creation_date = DateTime("2021-01-27")
        self.original.setEffectiveDate(DateTime("2021-02-09"))
        self.original.setExpirationDate(DateTime("2026-01-01"))
        transaction.commit()

    def duplicate(self, as_user=TEST_USER_ID):
        """Duplicate the original the way Volto's "Duplicate" does it.

        Volto posts to ``@copy``, which is ``manage_copyObjects`` +
        ``manage_pasteObjects`` - the same code path, without the HTTP layer.
        """
        container = self.original.aq_parent
        with mock.patch.object(
            events.user, "get_current", return_value=FakeMember(as_user)
        ):
            clipboard = container.manage_copyObjects(ids=[self.original.getId()])
            new_id = container.manage_pasteObjects(cb_copy_data=clipboard)[0]["new_id"]
        transaction.commit()
        return container[new_id]

    def test_creator_is_the_user_that_duplicated(self):
        copy = self.duplicate(as_user="andreea")
        self.assertEqual(("andreea",), copy.creators)
        self.assertEqual("andreea", copy.Creator())

    def test_creation_date_is_not_inherited(self):
        copy = self.duplicate()
        self.assertNotEqual(self.original.creation_date, copy.creation_date)
        self.assertTrue(
            copy.creation_date > DateTime() - timedelta(minutes=5),
            "the copy should look newly created, got %s" % copy.creation_date,
        )

    def test_publication_and_expiration_dates_are_cleared(self):
        copy = self.duplicate()
        self.assertIsNone(copy.effective_date)
        self.assertIsNone(copy.expiration_date)
        # ... while the original keeps its own dates
        self.assertEqual(
            DateTime("2021-02-09"), self.original.effective_date.toZone("UTC")
        )
        self.assertIsNotNone(self.original.expiration_date)

    def test_content_and_contributors_are_preserved(self):
        copy = self.duplicate()
        self.assertEqual("Original", copy.title)
        self.assertEqual(("someoneelse",), copy.contributors)

    def test_copy_without_a_real_author_keeps_the_original_provenance(self):
        """Imports, content rules and anonymous traversal must not invent an
        author out of a non-member."""
        copy = self.duplicate(as_user="anonymous_user")
        self.assertEqual(("costasil",), copy.creators)
        self.assertEqual(self.original.creation_date, copy.creation_date)


class TestCatalogProvenance(unittest.TestCase):
    """The wrong creator was visible to editors through the catalog, which is
    what feeds the listings and the notification."""

    layer = EEA_CLIMATEADAPT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Document", "original", title="Original")
        self.original = self.portal["original"]
        self.original.creators = ("costasil",)
        self.original.creation_date = DateTime("2021-01-27")
        transaction.commit()

    def test_copy_is_indexed_with_the_new_creator_and_date(self):
        container = self.original.aq_parent
        with mock.patch.object(
            events.user, "get_current", return_value=FakeMember("andreea")
        ):
            clipboard = container.manage_copyObjects(ids=[self.original.getId()])
            new_id = container.manage_pasteObjects(cb_copy_data=clipboard)[0]["new_id"]
        transaction.commit()

        brain = self.portal.portal_catalog(UID=container[new_id].UID())[0]
        self.assertEqual("andreea", brain.Creator)
        self.assertTrue(brain.CreationDate > DateTime("2026-01-01"))
