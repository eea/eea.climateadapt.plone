# Climate-ADAPT Authentication & Authorization Setup

## Overview

Climate-ADAPT uses **Eionet LDAP** as the central user and group directory, integrated with Plone via `Products.LDAPUserFolder`. Access control is managed through **local roles** assigned to LDAP groups (and individual users) on specific content folders.

## Authentication

- **User source**: Eionet LDAP (`Products.LDAPUserFolder` configured as `ldap-plugin` in the root `acl_users`)
- **Groups**: Synced from Eionet LDAP, using the `extranet-cca-*` naming convention
- **Login**: Users authenticate against LDAP; group membership is resolved on each request

## LDAP Groups

All LDAP groups use the `extranet-cca-*` prefix. Two categories exist:

### Site-wide groups

| Group | Purpose |
|-------|---------|
| `extranet-cca-managers` | Site managers (full site access) |
| `extranet-cca-editors` | General content editors |
| `extranet-cca-reviewers` | Content reviewers |
| `extranet-cca-checkers` | Content checkers |
| `extranet-cca-powerusers` | Power users (metadata content creation) |

### Section-specific groups

| Group | Section |
|-------|---------|
| `extranet-cca-mission` | EU Mission on Adaptation (core team) |
| `extranet-cca-missionext` | EU Mission (external contributors) |
| `extranet-cca-newsevents` | News & events editors |
| `extranet-cca-observatory` | Climate Adaptation Observatory editors |
| `extranet-cca-sandbox` | Sandbox area access |
| `extranet-cca-ma` / `-ma-managers` / `-ma-contacts` | Covenant of Mayors |
| `extranet-cca-thematicexperts` | Thematic experts (sector-filtered email lookups) |

### Local groups

A migration (`migrate_eionet_groups` script) exists to replace `extranet-*` references with `local-*` groups. Some locations already use `local-*` groups.

## Authorization — Local Roles by Location

Roles are assigned via **local roles** on content folders. Below is the current assignment map.

### Portal root (`/cca`)

| Principal | Roles |
|-----------|-------|
| `extranet-cca-managers` | Manager |
| `extranet-cca-editors` | Reader |
| `extranet-cca-reviewers` | Contributor, Reviewer |
| `extranet-cca-checkers` | Reader |
| `castechi` | Reviewer, Reader |

### English root (`/cca/en`)

| Principal | Roles |
|-----------|-------|
| `extranet-cca-managers` | Contributor, Reviewer, Editor, Reader |
| `extranet-cca-reviewers` | Contributor, Reviewer, Editor, Reader |
| `moskysas` | Contributor, Reviewer, Editor, Reader |

### EU Mission (`/cca/en/mission`) — inheritance blocked

| Principal | Roles |
|-----------|-------|
| `yilmabek` | Manager |
| `extranet-cca-mission` | Contributor, Reviewer, Editor, Reader |
| `extranet-cca-missionext` | Reader |
| `AuthenticatedUsers` | Reader |

Sub-sections under `/mission` grant edit access to `-missionext` for: `external-content`, `sandbox`, `community-of-practice`, `events`, `funding`. News sub-sections grant full edit to both `-mission` and `-missionext`.

### Observatory (`/cca/en/observatory`)

| Principal | Roles |
|-----------|-------|
| `extranet-cca-observatory` | Contributor, Reviewer, Editor, Reader |
| `brandcor` | Reader |
| `karadgu` | Reader |
| `smithann` | Contributor, Reviewer, Editor, Reader |

### Metadata sections (`/cca/en/metadata/*`)

All metadata sub-sections (case-studies, adaptation-options, projects, indicators, organisations, tools, portals, map-graphs, guidances, publications, videos) follow the same pattern:

| Principal | Roles |
|-----------|-------|
| `extranet-cca-powerusers` | Contributor, Reviewer, Editor, Reader |
| `volleson` | Contributor, Reviewer, Editor, Reader |
| `AuthenticatedUsers` | Contributor, Reader |

The parent `/cca/en/metadata` also grants `extranet-cca` → Contributor.

### News & Events

| Location | Principal | Roles |
|----------|-----------|-------|
| `/cca/en/news-archive` | `extranet-cca-newsevents` | Contributor, Reviewer, Editor, Reader |
| `/cca/en/news-archive` | `extranet-cca-editors` | Contributor, Editor |
| `/cca/en/more-events` | `extranet-cca-newsevents` | Contributor, Reviewer, Editor |
| `/cca/en/more-events` | `AuthenticatedUsers` | Contributor |

### Other sections

| Location | Principal | Roles |
|----------|-----------|-------|
| `/cca/en/sandbox` | `extranet-cca-sandbox` | Contributor, Reviewer, Editor, Reader |
| `/cca/en/sandbox` | `extranet-cca-editors` | Contributor, Editor, Reader |
| `/cca/en/content-management-center` | `yilmabek` | Reader, Editor, Contributor, Reviewer |
| `/cca/en/eu-adaptation-policy/covenant-of-mayors/city-profile` | `extranet-cca-ma-managers` | Contributor, Reviewer, Editor |

Most remaining `/cca/en/*` sections (about, measures, projects, countries-regions, knowledge, etc.) grant `extranet-cca-editors` → Contributor, Editor.

## Open Access Patterns

Some locations grant roles to `AuthenticatedUsers`:

- `/cca/en/mission` and sub-sections → Reader (public-facing mission content)
- `/cca/en/metadata/*` → Contributor, Reader (allows any logged-in user to submit content)
- `/cca/en/more-events` → Contributor
- `/cca/en/news-archive/news` → Contributor

## Group Email Lookups

`stringinterp.py` registers Plone string interpolation substitutions for group email lookups. These are used in notification templates:

| Substitution | Group |
|-------------|-------|
| `cca_ma` | `extranet-cca-ma` |
| `cca_ma_contacts` | `extranet-cca-ma-contacts` |
| `cca_ma_managers` | `extranet-cca-ma-managers` |
| `cca_newsevents` | `extranet-cca-newsevents` |
| `cca_powerusers` | `extranet-cca-powerusers` |
| `cca_reviewers` | `extranet-cca-reviewers` |
| `cca_managers` | `extranet-cca-managers` |
| `cca_checkers` | `extranet-cca-checkers` |
| `cca_editors` | `extranet-cca-editors` |
| `cca_thematicexperts` | `extranet-cca-thematicexperts` (sector-filtered) |

## Management Scripts

| Script | Purpose |
|--------|---------|
| `report_roles` | Generates CSV/console report of all local role assignments |
| `migrate_eionet_groups` | Migrates `extranet-*` → `local-*` group references in local roles |
| `export_active_users` | Exports user IDs active in the last N years |

## Notes

- Translation folders (`/ro`, `/de`, etc.) inherit permissions from `/en` and are auto-synced; local roles are only managed on English content.
- The `extranet-*` → `local-*` migration is a work in progress; both naming conventions coexist.
- Individual user local roles (e.g., `yilmabek`, `moskysas`) are ad-hoc grants for specific editors not covered by group assignments.
