# Fix Mission Block Links

These are two Zope command-line utilities designed to repair Volto block references
(images, links, teasers) that broke when the `/en/mission` tree was reorganised on
production in June 2026.

- `export_uid_paths` runs against a database that **still has** the old content (the
  development database is such a copy) and exports the dictionary "UID → path it used
  to have".
- `fix_mission_block_links` runs against the reorganised database (production) and
  rewrites the dead references in place, dry-run by default.

## Rationale

| Old location | What happened on production | UIDs |
|---|---|---|
| `/en/mission` (Subsite) | renamed to `/en/mission-inactive` | preserved |
| `/en/mission` | new Redirection (301) to `https://mission-adaptation-portal.ec.europa.eu/` | new object |
| `the-mission`, `mission-projects`, `knowledge-and-data`, `funding`, `events`, `community-of-practice`, `newsletter-signup` | replaced by Redirections to the external mission portal, content deleted from Climate-ADAPT | gone |
| `knowledge-and-data/regional-adaptation-support-tool/**` (RAST) | re-created under `/en/eu-policy/eu-adaptation-policy/eu-mission-on-adaptation/regional-adaptation-support-tool` (plus `adaptation-dashboard`, `signatory-reporting`, `images`) | **all new** |

Because the RAST tree was **re-created instead of moved**, every block reference that
stored an old UID is dead. An audit of the new mission subtree on production found 112
internal references, **59 of them dead, 57 of those in the `item` block's `image`
field**. (That audit was done over the REST API and silently skipped pages whose
`blocks` could not be fetched, so treat 59 as a lower bound — the dry-run CSV is the
authoritative number.)

A reference keeps working after the reorganisation only when it is stored as a **path**
and `plone.app.redirector` has an alias for it. References stored as
`resolveuid/<uid>` have nothing to fall back on.

Note: the number of `../` in `../../../../resolveuid/<uid>` is irrelevant — the
browser clamps at the site root and `plone.outputfilters` registers a `resolveuid`
view `for="*"` that 301-redirects to the target. Broken images are a **dead UID**
problem, not a relative-path problem.

## Features

- **Dry-run by default**: nothing is written without `--apply`.
- **Structured traversal, not string search/replace**: blocks are walked the same way
  `plone.restapi.blocks.visit_blocks` walks them, including subblocks inside `columns`
  and `tabs`, and slate `children`/`uploads`.
- **Every reference form is understood**: `resolveuid/<uid>`, absolute internal URLs
  (`https://climate-adapt.eea.europa.eu/...`), root-relative paths, and the same three
  with a traversal suffix (`/@@images/image/big`, `/@@download/file`).
- **The original form is preserved**: a `resolveuid` reference stays `resolveuid`
  (re-encoded with the new UID via `path2uid`), an absolute URL stays an absolute URL.
- **Three ways to recover the old target**: the UID map; the block-join map (block ids
  survive a copy, so "what did this exact block point at in the pre-reorg copy of this
  page?" answers even when the UID is gone); and the path already inside the value.
- **Alias-aware**: old → new is resolved through `IRedirectionStorage`, following
  alias chains, with an `id`-based fallback for aliases whose target folder was also
  renamed (e.g. `images/step-1.3` → `images/1.3`).
- **Bounded blast radius**: only references whose *old* path is under `--restrict`
  are touched; the defaults are English-only.
- **No side effects on the translation pipeline**: see Safety below.
- **CSV report** of every decision, taken or skipped.

## How to Run

Both scripts are registered console scripts (`eea.climateadapt.scripts` entry points),
so they are available as `bin/export_uid_paths` and `bin/fix_mission_block_links`. If
they are missing, the package was not reinstalled after the entry points were added:

```bash
bin/pip install -r requirements-mxdev.txt
```

Alternatively run them as modules, which needs no installation:

```bash
/app/bin/python3 -m eea.climateadapt.scripts.export_uid_paths ...
/app/bin/python3 -m eea.climateadapt.scripts.fix_mission_block_links ...
```

### Step 1 — export the dictionary (run on the pre-reorg database)

```bash
make export-mission-uid-map
# equivalent to:
docker compose exec backend /app/docker-entrypoint.sh \
    bin/export_uid_paths --portal cca --zope-conf etc/relstorage.conf \
    --out mission_uid_paths.json --block-join mission_block_join.json
```

Against the current development database this yields ~23k UID entries over 24
languages and ~7.4k objects / ~46k block references. Copy both JSON files to the
machine where step 2 runs.

### Step 2 — audit on production (writes nothing)

```bash
make fix-mission-links ARGS="--csv /tmp/mission_block_links_report.csv"
# equivalent to:
docker compose exec backend /app/docker-entrypoint.sh \
    bin/fix_mission_block_links --portal cca --zope-conf etc/relstorage.conf \
    --uid-map mission_uid_paths.json --block-join mission_block_join.json \
    --csv mission_block_links_report.csv
```

### Step 3 — review the CSV, then apply

```bash
make fix-mission-links-run ARGS="--csv /tmp/mission_block_links_report.csv"
```

## Arguments

### `export_uid_paths`

| Argument | Default | Description |
|---|---|---|
| `--portal` | required | Portal ID (`cca`) |
| `--zope-conf` | required | Path to `zope.conf` (`etc/relstorage.conf`) |
| `--path` | `/*/mission` | Portal-relative subtree to export; `*` expands to every language folder. Repeatable |
| `--out` | required | Output JSON `{uid: portal-relative path}` |
| `--block-join` | – | Also dump `{old object path: [{block_id, field, target}]}` to this file |
| `--all` | off | Export every catalog brain instead of only `IBlocks` objects |
| `--verbose` | off | Log every object scanned |

### `fix_mission_block_links`

| Argument | Default | Description |
|---|---|---|
| `--portal` | required | Portal ID (`cca`) |
| `--zope-conf` | required | Path to `zope.conf` |
| `--uid-map` | required | JSON `{uid: old path}` produced by step 1 |
| `--block-join` | – | JSON block map from step 1 (fallback lookup) |
| `--path` | `/en/eu-policy/eu-adaptation-policy/eu-mission-on-adaptation`, `/en/mission-inactive` | Subtrees to scan; `*` = language code. Repeatable |
| `--restrict` | `/en/mission` | Only rewrite references whose **old** path starts with this prefix |
| `--normalize-aliasable` | off | Also rewrite references that currently resolve only thanks to an alias (they work, but they depend on the aliases surviving) |
| `--rewrite-text` | off | Also rewrite URLs inside slate display text (`text`/`plaintext`) |
| `--no-alt-match` | off | Disable pairing a dead reference with an image using the block's `alt` text (see *Alt-text pairing*) |
| `--traverse` | off | Enumerate objects by walking the tree instead of using the catalog |
| `--apply` | off | Write the changes |
| `--limit` | 0 (no limit) | Stop after N objects |
| `--commit-every` | 50 | Commit every N changed objects |
| `--csv` | – | Report path |

The defaults are **English only** on purpose — the site is multilingual and the other
23 language copies were not reorganised. To widen the scan, pass
`--path '/*/eu-policy/eu-adaptation-policy/eu-mission-on-adaptation'` together with
`--restrict '/*/mission'`.

## Implementation Details

- Block walking lives in `_blocks.py` (`iter_blocks`, `iter_strings`, `classify`,
  `split_suffix`, `subblocks`) and is shared with the exploration scripts.
- `classify` only accepts real content references. Strings that merely *look* internal
  — the site root `/`, a bare host root, external hosts, anything unrecognised — are
  ignored instead of being reported.
- Object enumeration uses the catalog (`object_provides=plone.restapi.behaviors.IBlocks`
  + `path`) unless `--traverse` is given.
- For each reference the script: classifies the value → skips it if the target still
  resolves → recovers the **old** path → maps old → new through
  `IRedirectionStorage` → rewrites, preserving the original form and any traversal
  suffix.
- `resolveuid` values are re-encoded with `plone.restapi.deserializer.utils.path2uid`.
- A reference whose new target is a `Link`/`Redirection` pointing outside
  `*.eea.europa.eu` is reported as `LEFT-CCA` and **not** rewritten — the content left
  Climate-ADAPT and only an editor can decide the replacement.
- **Safety**: `blocks` is mutated in place and `_p_changed` is set. No lifecycle events
  are fired and `request.disable_object_modified_handler = True` is set, so content
  rules and the eTranslation pipeline (`TRANSLATE_ON_CHANGE`) are not triggered. No
  reindexing is performed — URL text does not affect catalog metadata (do a separate
  reindex pass if you also use `--rewrite-text`).
- **Acquisition pitfall** (relevant to `--traverse`): never call `node.items()` /
  `node.objectValues()` or read `node.blocks` unguarded during a physical walk. For
  non-folderish content those attributes are *acquired* from the parent folder, which
  makes every image look like it carries blocks and makes the walk loop forever. The
  script gates descent with `IDexterityContainer.providedBy(node)`, reads attributes
  through `aq_base(node)`, and keeps a visited set.

### Alias resolution is per object, not per subtree

`IRedirectionStorage` holds an alias for each **moved object**, not for everything
below it. Production aliases `…/regional-adaptation-support-tool` and
`…/regional-adaptation-support-tool/images`, but not the leaf folders (`images/1.1`)
or the images themselves. Following the alias of the exact path therefore finds
nothing for `…/images/1.1/map-mission.png`. `ancestor_alias()` walks up to the
nearest aliased ancestor, rebuilds the remainder and **verifies the candidate by
traversal** before accepting it.

### Alt-text pairing

A dead `resolveuid/<uid>` carries no file name, and image blocks usually have no
`image_scales` either, so a UID missing from the pre-reorg dictionary cannot be
mapped by path. But editors routinely store the original upload name in the block's
`alt`:

```json
{"@type": "image", "alt": "Step1_3_ex3_1.png",
 "url": "../../../../../../../resolveuid/ba029abf391340d68eac92470e334aaf"}
```

and the reorganisation kept the images at the same relative paths. The script
indexes every `Image`/`File` id under the scanned subtrees, normalises both sides
(lower case, accents stripped, spaces/underscores and `@` folded to dashes, and dots
folded to dashes for names like `Asset 70@1.5x.png` -> `asset-70-1-5x.png`) and
rewrites **only when exactly one object matches**. If the same file name exists both
inside the page's own folder and in a shared images folder, the child of the
referencing page wins — that is where Volto stores an inline upload. Anything still
ambiguous is reported, never guessed. Disable with `--no-alt-match`.

### Path forms: portal-relative vs physical

`IRedirectionStorage.redirects()` returns **physical** paths (`/cca/en/…`) while the
block-join map is keyed portal-relative (`/en/…`); the catalog `path` index needs the
**physical** path while the scan roots are portal-relative. Both mismatches fail
silently with zero matches, so any new lookup has to pick the form explicitly.

## Output Format (Console Example)

Real output of a dry-run against the development database (`--path /en/mission`,
i.e. the *pre-reorg* copy — which is why nothing needs fixing there and almost
everything is `ALIVE`):

```
INFO fixer: en/mission -> 690 block objects

Scanned block objects: 690
  FIXED              0
  ALIVE              754
  ALIVE-VIA-ALIAS    1
  UNRESOLVED         1
  LEFT-CCA           0
  NOT-IN-MAP         57
  OUT-OF-SCOPE       4
  TEXT-OCCURRENCE    3
  objects written: 0 (dry-run: True)
report: /tmp/mission_block_links_report.csv
```

Against production the same run produces `FIXED` rows for the dead references and
`LEFT-CCA` rows for the content that moved to the external mission portal.

The CSV has one row per decision:

| Column | Meaning |
|---|---|
| `action` | `FIXED`, `ALIVE`, `ALIVE-VIA-ALIAS`, `UNRESOLVED`, `LEFT-CCA`, `NOT-IN-MAP`, `OUT-OF-SCOPE`, `TEXT-OCCURRENCE` |
| `object` | Portal-relative path of the object holding the block |
| `container` | Where inside the block the value was found (`image`, `items.3`, `data.rastBlock.items.2.title`) |
| `block_id`, `block_type`, `field` | Block identification |
| `kind` | `resolveuid`, `absolute-internal` or `root-relative` |
| `old`, `new` | Value before / after (`new` is empty in a dry-run row that was not fixed) |
| `note` | How the old path was recovered (`uid-map`, `block-join`, `value`) and how the new one was found (`alias`, `alias+id`, `id`, `unchanged`), or why nothing was done (`left-cca`, `unresolved`, `uid-not-in-map`) |

`ALIVE` references produce no rows — they are counted only.

## Rehearsing on a Development Database

`rehearse_reorg.py` (run with `python -m`, it is not a registered console script)
reproduces the production situation in `/en/sandbox`: it builds a page whose blocks
reference an image three ways (`image` block via `resolveuid`, `item` block via
absolute URL, `callToActionBlock` via `resolveuid…/@@images/image/big`), copies the
subtree (which mints new UIDs), deletes the original and registers the aliases
production has — i.e. exactly the failure seen on the live site.

```bash
docker compose exec -T -e TRANSLATE_ON_CHANGE= backend /app/docker-entrypoint.sh \
    /app/bin/python3 -m eea.climateadapt.scripts.rehearse_reorg setup
# prints src_id / dst_id / pic_uid_before; writes /tmp/rehearse_manifest.json
# and /tmp/rehearse_uid_map.json

docker compose exec -T -e TRANSLATE_ON_CHANGE= backend /app/docker-entrypoint.sh \
    /app/bin/python3 -m eea.climateadapt.scripts.fix_mission_block_links \
    --portal cca --zope-conf etc/relstorage.conf \
    --uid-map /tmp/rehearse_uid_map.json \
    --path /en/sandbox/<dst_id> --restrict /en/sandbox --traverse \
    --csv /tmp/rehearse_report.csv            # add --apply to write

docker compose exec -T backend /app/docker-entrypoint.sh \
    /app/bin/python3 -m eea.climateadapt.scripts.rehearse_reorg verify
docker compose exec -T -e TRANSLATE_ON_CHANGE= backend /app/docker-entrypoint.sh \
    /app/bin/python3 -m eea.climateadapt.scripts.rehearse_reorg cleanup
```

Verified result: all three references go from `DEAD` to `ALIVE`, pointing at the
copied image, with the `/@@images/image/big` suffix preserved.

`TRANSLATE_ON_CHANGE=` must be unset for setup/cleanup: creating and deleting content
fires events that queue `sync_paths` jobs in Redis.

## Results on production (October 2026 run)

| stage | `FIXED` | `UNRESOLVED` | `NOT-IN-MAP` |
|---|---|---|---|
| first audit, exact path mapping only | 7 | 110 | 107 |
| + ancestor aliases and the catalog path fix | 83 | 34 | 107 |
| + alt-text pairing | 27 more | 34 | 80 |
| + block-join path form fix | 4 more | 34 | 76 |

114 references rewritten across 42 objects, all verified to render
(`200 image/png` / `200 image/jpeg`). What remains is 76 `NOT-IN-MAP` (78 of the
original 107 have no `alt` at all) and 34 `UNRESOLVED` pointing at content that left
for the external mission portal.

## Limitations

- References whose old content was deleted **and** replaced by a Redirection to the
  external mission portal cannot be repaired automatically; they are reported as
  `LEFT-CCA`.
- Images that lived *inside* a page folder (e.g.
  `step-1-1/24198_eea_rast_step-01_…png`) were never copied — there is nothing to
  point at, so they must be re-uploaded by editors.
- Some references were already broken **before** the reorganisation (their UIDs are
  missing from both the development and the production database). They show up as
  `NOT-IN-MAP` / `UNRESOLVED` and are not caused by this migration. On the dev
  snapshot that is 11 distinct UIDs behind 57 rows, and two of them account for 46 of
  those rows (they are repeated across the RAST pages) — so it is ~11 editor
  decisions, not 57.
- The development database is a pre-reorg copy with later local edits; it resolved 49
  of the 51 dead UIDs found in the production `/en` mission subtree. The remaining two
  are reported, never guessed.
- URLs inside rich text are display text; they are reported (`TEXT-OCCURRENCE`) and
  left alone unless `--rewrite-text` is passed.

## Troubleshooting

- **`ModuleNotFoundError: eea.climateadapt`** — run from the `backend/` directory so
  that `sources/` is added to `PYTHONPATH` by `docker-entrypoint.sh`.
- **The fixer finds 0 objects although the content is there** — the catalog is stale
  for that content (this happens on the development database, where freshly created
  content is not indexed even after `reindexObject()`). Use `--traverse`.
- **`NOT-IN-MAP` for a UID you expected** — the UID predates the export scope. Widen
  `--path` of `export_uid_paths`, or check whether the object ever existed in this
  database.
- **A `FIXED` row whose `new` value still does not render** — check that the target
  object has the image itself; `/@@images/image/big` requires an image with that
  scale.

## Exploration Tools

Kept in this directory for re-auditing (they are probes, not supported tooling):

| Script | Purpose |
|---|---|
| `scan_block_links.py` | Dump every internal reference found in blocks under a subtree, with counts per block type/field |
| `analyze_mission_refs.py` | Cross-check those references against the catalog and the redirect storage |
| `check_dead_uids.py` | Resolve a list of UIDs and report alive/dead |
| `check_apis.py` | Verify the `IRedirectionStorage` / `path2uid` / catalog assumptions used by the fixer |
| `check_rewrite.py` | Unit-style check of the value rewriting for all reference forms |

## Lessons Learnt

- `resolveuid` is resolved by a view registered `for="*"`, so relative depth in the
  value never matters — always suspect a dead UID before suspecting the path.
- Renaming a folder preserves UIDs; **copying content mints new ones**. A "move" done
  as copy + delete breaks every UID-based reference while path-based references keep
  working through aliases, which is why the damage looks selective.
- Aliases are not a fix: they are a dependency. `…/images/step-1.3/x.jpg` aliases to a
  folder that was renamed to `images/1.3` at the destination, so some alias chains stop
  halfway.
- Never trust `node.items()` during a physical walk — see the acquisition pitfall
  above; it produced an infinite loop that looked like a slow script.
