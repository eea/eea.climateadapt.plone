"""Local roles reporting logic"""

import logging

logger = logging.getLogger(__name__)

from plone.app.multilingual.interfaces import ILanguageRootFolder
from plone.base.interfaces import IPloneSiteRoot
from plone.dexterity.interfaces import IDexterityContent

IGNORED_USER_IDS = [
    "admin",
    "eugentripon",
    "eugentripon",
    "ghicaale",
    "ghitab",
    "iuliantest",
    "krisztina",
    "tiberich",
    "tibi",
    "tibiadmin",
    "tibitest",
    "tripodor",
    "zopeadmin",
]


def get_roles_data(obj, path, include_owner=False):
    roles = obj.get_local_roles()
    filtered_roles = []

    for principal, role_list in roles:
        if principal in IGNORED_USER_IDS:
            continue

        if not include_owner:
            role_list = [r for r in role_list if r != "Owner"]

        if role_list:
            filtered_roles.append((principal, role_list))

    blocked = getattr(obj, "__ac_local_roles_block__", False)
    return {
        "path": path,
        "roles": filtered_roles,
        "blocked": bool(blocked),
    }


def get_local_roles_report(portal, include_owner=False):
    """Run the reporting logic and return data."""

    # Initial paths to start recursion from
    start_paths = [
        "",  # portal root
        "en",
        "en/mission",
        "en/observatory",
    ]

    all_data = []
    seen_paths = set()
    portal_id = portal.getId()

    # Use a stack for iterative traversal to be robust against RecursionError
    # and to allow better error handling per object.
    stack = []

    for rel_path in start_paths:
        try:
            if not rel_path:
                obj = portal
            else:
                obj = portal.unrestrictedTraverse(rel_path)
            stack.append((obj, rel_path))
        except Exception as e:
            logger.warning(f"Could not access start path '{rel_path}': {e}")

    while stack:
        obj, current_rel_path = stack.pop()

        full_path = (
            "/" + portal_id + (f"/{current_rel_path}" if current_rel_path else "")
        )

        if full_path in seen_paths:
            continue
        seen_paths.add(full_path)

        try:
            data = get_roles_data(obj, full_path, include_owner=include_owner)
            # Include any object that has local roles or blocked inheritance
            if data["roles"] or data["blocked"]:
                all_data.append(data)
        except Exception as e:
            logger.error(f"Error getting roles data for {full_path}: {e}")
            continue

        # Recurse into children if it's folder-like
        if hasattr(obj, "objectValues"):
            try:
                children = obj.objectValues()
            except Exception as e:
                logger.error(f"Error getting children for {full_path}: {e}")
                continue

            for child in children:
                try:
                    child_id = child.getId()
                except Exception as e:
                    logger.error(f"Error getting ID for child of {full_path}: {e}")
                    continue

                # Filter for content objects: must be Dexterity content or the portal root
                if not (
                    IDexterityContent.providedBy(child)
                    or IPloneSiteRoot.providedBy(child)
                ):
                    continue

                # For Climate-ADAPT, we want to skip the translation folders
                # if they are at the root level (except for 'en').
                if not current_rel_path and child_id != "en":
                    try:
                        if ILanguageRootFolder.providedBy(child):
                            continue
                    except Exception:
                        # Fallback if interface check fails
                        if len(child_id) == 2:
                            continue

                child_rel_path = f"{current_rel_path}/{child_id}" if current_rel_path else child_id
                stack.append((child, child_rel_path))

    return all_data
