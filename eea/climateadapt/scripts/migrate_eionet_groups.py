"""Migrate extranet- groups to local- groups in local roles"""

import argparse
import logging
import transaction

import Zope2
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.users import system as system_user
from Testing.makerequest import makerequest
from Zope2.Startup.run import make_wsgi_app

from zope.component.hooks import setSite
from zope.globalrequest import setRequest
from plone.base.interfaces import IPloneSiteRoot
from plone.dexterity.interfaces import IDexterityContent
from Products.CMFCore.utils import getToolByName


logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser(
    prog="MigrateEionetGroups",
    description="Migrate local roles from extranet- groups to local- groups",
)

parser.add_argument(
    "--portal",
    dest="portal_id",
    required=True,
    help="Portal ID",
)

parser.add_argument(
    "--zope-conf",
    dest="zope_conf",
    required=True,
    help="Path to zope.conf",
)

parser.add_argument(
    "--run",
    action="store_true",
    help="Commit changes to the database",
)


def migrate_local_roles(obj, dry_run=True):
    """Detect extranet- groups and assign roles to corresponding local- groups."""
    changed = False
    local_roles = obj.get_local_roles()
    portal_groups = getToolByName(obj, "portal_groups")

    for principal, roles in local_roles:
        if principal.startswith("extranet-"):
            new_principal = principal.replace("extranet-", "local-")

            # Check if new_principal already has these roles
            existing_roles = dict(local_roles).get(new_principal, [])
            if set(roles).issubset(set(existing_roles)):
                continue

            # Combine roles if new_principal already exists in local roles
            final_roles = list(set(roles) | set(existing_roles))

            print(
                f"  Migrating {principal} -> {new_principal} on {obj.absolute_url(1)}"
            )
            print(f"    Roles: {', '.join(final_roles)}")

            if not dry_run:
                # Ensure group exists
                if not portal_groups.getGroupById(new_principal):
                    print(f"    Creating group: {new_principal}")
                    portal_groups.addGroup(new_principal)

                obj.manage_setLocalRoles(new_principal, final_roles)
                changed = True

    return changed


def run(app):
    """Run the migration script."""
    args = parser.parse_args()
    dry_run = not args.run

    try:
        portal = app[args.portal_id]
    except KeyError:
        print(f"Error: Portal '{args.portal_id}' not found.")
        return

    setSite(portal)

    # We start from the portal root and crawl everything
    stack = [(portal, "")]
    seen_paths = set()
    total_objects = 0
    modified_objects = 0

    print(f"Starting migration (dry_run={dry_run})...")

    while stack:
        obj, current_rel_path = stack.pop()
        try:
            path = obj.absolute_url(1)
        except Exception:
            path = current_rel_path

        if path in seen_paths:
            continue
        seen_paths.add(path)
        total_objects += 1

        if total_objects % 1000 == 0:
            print(f"Processed {total_objects} objects...")

        try:
            if migrate_local_roles(obj, dry_run=dry_run):
                modified_objects += 1
        except Exception as e:
            logger.error(f"Error processing {path}: {e}")

        # Recurse into children if it's folder-like. We use objectIds() + _getOb()
        # instead of objectValues() because the latter returns a Lazy sequence
        # that calls _getOb internally. If a folder has a broken order key
        # (an ID present in the ordering but missing from the BTree), _getOb
        # raises AttributeError mid-iteration, crashing the entire traversal.
        # By retrieving each child individually we can skip just the broken
        # child and continue processing the rest of the folder.
        if hasattr(obj, "objectIds"):
            try:
                child_ids = obj.objectIds()
            except Exception as e:
                logger.error(
                    f"Error getting child IDs for {path}: {e}. Skipping folder."
                )
                continue

            for child_id in child_ids:
                try:
                    child = obj._getOb(child_id)
                except (AttributeError, KeyError) as e:
                    logger.error(
                        f"Broken order key '{child_id}' in {path}: {e}. "
                        f"Skipping this child."
                    )
                    continue
                except Exception as e:
                    logger.error(
                        f"Error getting child '{child_id}' from {path}: {e}. "
                        f"Skipping this child."
                    )
                    continue

                # Filter for content objects: must be Dexterity content or the portal root
                if not (
                    IDexterityContent.providedBy(child)
                    or IPloneSiteRoot.providedBy(child)
                ):
                    continue

                child_rel_path = (
                    f"{current_rel_path}/{child_id}" if current_rel_path else child_id
                )
                stack.append((child, child_rel_path))

    print(f"\nMigration finished.")
    print(f"Total objects processed: {total_objects}")
    print(f"Total objects modified: {modified_objects}")

    if not dry_run:
        transaction.commit()
        print("Transaction committed.")
    else:
        print("Dry run finished. No changes were committed.")


def main():
    args = parser.parse_args()
    make_wsgi_app({}, args.zope_conf)
    app = Zope2.app()
    app = makerequest(app)
    app.REQUEST["PARENTS"] = [app]
    setRequest(app.REQUEST)
    newSecurityManager(None, system_user)
    run(app)


if __name__ == "__main__":
    main()
