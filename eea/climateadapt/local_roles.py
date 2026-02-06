"""Local roles reporting logic"""

import logging

logger = logging.getLogger(__name__)

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

    def traverse(obj, current_rel_path):
        full_path = (
            "/" + portal_id + (f"/{current_rel_path}" if current_rel_path else "")
        )
        if full_path in seen_paths:
            return
        seen_paths.add(full_path)

        data = get_roles_data(obj, full_path, include_owner=include_owner)
        # Include any object that has local roles or blocked inheritance
        if data["roles"] or data["blocked"]:
            all_data.append(data)

        # Recurse into children if it's folder-like
        if hasattr(obj, "objectValues"):
            for child in obj.objectValues():
                id = child.getId()
                # Skip some obviously uninteresting system folders/objects if they appear
                if id in ["portal_catalog", "portal_workflow", "portal_types"]:
                    continue

                # For Climate-ADAPT, we want to skip the translation folders during recursion
                # if they are at the root level (e.g., /cca/ro, /cca/de)
                # except for 'en' which is our starting point anyway.
                if not current_rel_path and id in [
                    "bg",
                    "cs",
                    "da",
                    "de",
                    "el",
                    "es",
                    "et",
                    "fi",
                    "fr",
                    "ga",
                    "hr",
                    "hu",
                    "it",
                    "lt",
                    "lv",
                    "mt",
                    "nn",
                    "nl",
                    "pl",
                    "pt",
                    "ro",
                    "sk",
                    "sl",
                    "sv",
                ]:
                    continue

                child_rel_path = f"{current_rel_path}/{id}" if current_rel_path else id
                traverse(child, child_rel_path)

    for rel_path in start_paths:
        try:
            if not rel_path:
                obj = portal
            else:
                obj = portal.unrestrictedTraverse(rel_path)
            traverse(obj, rel_path)
        except Exception as e:
            logger.warning(f"Could not access path '{rel_path}': {e}")

    return all_data
