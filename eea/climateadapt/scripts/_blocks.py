"""Shared helpers for walking Volto blocks and classifying internal links.

Used by ``export_uid_paths`` and ``fix_mission_block_links``.

The traversal mirrors ``plone.restapi.blocks.visit_blocks`` (which handles
``["data"]["blocks"]`` and ``["blocks"]`` via the ``NestedBlocksVisitor``
IBlockVisitor subscriber) and additionally handles the ``columns`` shape used
by the columns/group blocks, so that "layout blocks" such as columns and tabs
are descended into consistently.
"""

import re
from urllib.parse import urlparse

RESOLVEUID_RE = re.compile(r"resolveuid/([a-fA-F0-9\-]+)")

# Same rule plone.restapi uses in ``deserializer.utils.path2uid``: a traversal
# suffix starts at ``/@@`` or at a fragment.
PATH_RE = re.compile(r"^(.*?)((?=/@@|#).*)?$")

# Keys that hold nested blocks; they are handled by iter_blocks instead.
NESTING_KEYS = ("blocks", "blocks_layout")

# kinds
RESOLVEUID = "resolveuid"
ABSOLUTE_INTERNAL = "absolute-internal"
ROOT_RELATIVE = "root-relative"
EXTERNAL = "external"
OTHER = "other"


def subblocks(block):
    """Yield ``(block_id, block, container)`` for the immediate subblocks."""
    data = block.get("data")
    if isinstance(data, dict) and isinstance(data.get("blocks"), dict):
        for bid, sub in data["blocks"].items():
            if isinstance(sub, dict):
                yield bid, sub, "data.blocks"
    inner = block.get("blocks")
    if isinstance(inner, dict):
        for bid, sub in inner.items():
            if isinstance(sub, dict):
                yield bid, sub, "blocks"
    columns = block.get("columns")
    if isinstance(columns, list):
        for index, column in enumerate(columns):
            if isinstance(column, dict) and isinstance(column.get("blocks"), dict):
                for bid, sub in column["blocks"].items():
                    if isinstance(sub, dict):
                        yield bid, sub, f"columns[{index}].blocks"


def iter_blocks(obj):
    """Yield ``(block_id, block, container)`` for every block of an object.

    Depth-first, cycle safe.
    """
    blocks = getattr(obj, "blocks", None)
    if not isinstance(blocks, dict):
        return
    seen = set()
    stack = [
        (bid, block, "") for bid, block in blocks.items() if isinstance(block, dict)
    ]
    while stack:
        bid, block, container = stack.pop()
        if id(block) in seen:
            continue
        seen.add(id(block))
        yield bid, block, container
        stack.extend(subblocks(block))


def iter_strings(block, prefix=""):
    """Yield ``(container_dict, key, field_path, value)`` for every string.

    The container dict is yielded so the caller can rewrite the value in place.
    Nested block containers are skipped (see :func:`iter_blocks`).
    """
    for key, value in block.items():
        if key in NESTING_KEYS:
            continue
        if isinstance(value, str):
            yield block, key, f"{prefix}{key}", value
        elif isinstance(value, dict):
            yield from iter_strings(value, f"{prefix}{key}.")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, dict):
                    yield from iter_strings(item, f"{prefix}{key}[{index}].")


def classify(value, internal_hosts=()):
    """Classify a block string.

    Returns ``(kind, key)`` where ``key`` is the UID for resolveuid values and
    the portal-relative path for internal path/URL values. Values that are not
    content references at all - the site root ``/``, a host root, or an
    unrecognised string - come back as ``(OTHER, None)``.
    """
    if not value or not isinstance(value, str):
        return OTHER, None

    if "resolveuid" in value:
        match = RESOLVEUID_RE.search(value)
        if match:
            return RESOLVEUID, match.group(1)
        return OTHER, None

    parsed = urlparse(value)
    if parsed.netloc:
        if parsed.netloc not in internal_hosts:
            return EXTERNAL, None
        after_host = value[value.index(parsed.netloc) + len(parsed.netloc) :]
        match = PATH_RE.match(after_host)
        key = (match.group(1) or "").rstrip("/")
        return (ABSOLUTE_INTERNAL, key) if key else (OTHER, None)
    if value.startswith("/"):
        match = PATH_RE.match(parsed.path)
        key = (match.group(1) or "").rstrip("/")
        return (ROOT_RELATIVE, key) if key else (OTHER, None)
    return OTHER, None


def split_suffix(value, uid=None, path=None):
    """Return the trailing part of a reference (``/@@images/image/big``, ``#frag``).

    For ``../resolveuid/<uid>/@@images/image/big`` we must keep the suffix when
    re-pointing the reference to another UID.
    """
    if uid:
        marker = f"resolveuid/{uid}"
        if marker in value:
            return value.split(marker, 1)[1]
        return ""
    if path:
        idx = value.find(path)
        if idx != -1:
            return value[idx + len(path) :]
    return ""
