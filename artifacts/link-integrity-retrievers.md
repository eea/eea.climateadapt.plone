# Specification: Volto Block Link Integrity Retrievers for Climate-ADAPT

## Overview
This specification describes the implementation of custom link integrity discovery for Volto blocks within the `eea.climateadapt` ecosystem. Its primary goal is to ensure that internal links stored in custom Volto block structures (specifically `object_list` fields) are correctly tracked by Plone's `zc.relation` catalog.

## The Problem
Plone's default block link integrity discovery (`plone.restapi.blocks_linkintegrity.GenericBlockLinksRetriever`) only automatically extracts links from three top-level fields:
1. `url`
2. `href`
3. `preview_image`

However, many custom Climate-ADAPT blocks store links in more complex or differently-named structures:
*   **Nested Lists**: `ContentLinks`, `RelevantAceContent`, and `ASTNavigation` use an `object_list` (usually named `items`) where each entry contains a link field named `source` or `href`.
*   **Custom Top-level Fields**: Some variations or shadowed blocks might use `linkTo` (standard Volto listing) or `image`.

Without custom retrievers, these links are invisible to Plone's link integrity system, leading to broken links when the target content is moved or deleted without warning.

## Implementation Detail

### 1. New Link Retriever Adapter
A new subscriber adapter `CCAObjectListLinksRetriever` has been implemented in:
`eea/climateadapt/restapi/blocks_linkintegrity.py`

#### Extraction Logic:
*   **Nested Items**: It iterates through the `items` list if present. For each dictionary item, it extracts internal links from `source`, `href`, and `url` fields.
*   **Additional Fields**: It also checks for top-level `linkTo` and `image` fields.
*   **Discovery**: It uses `plone.restapi.blocks_linkintegrity.get_urls_from_value` to correctly handle `resolveuid/` patterns within strings, dictionaries, or lists.

### 2. Registration
The retriever is registered as a subscriber to the `IBlockFieldLinkIntegrityRetriever` interface in:
`eea/climateadapt/restapi/configure.zcml`

```xml
  <subscriber
    factory=".blocks_linkintegrity.CCAObjectListLinksRetriever"
    provides="plone.restapi.interfaces.IBlockFieldLinkIntegrityRetriever"
  />
```

## Affected Blocks and Fields

| Block (@type) | Field Location | Covered by Default? | Covered by New Retriever? |
| :--- | :--- | :--- | :--- |
| `ContentLinks` | `items[*].source` | No | **Yes** |
| `RelevantAceContent` | `items[*].source` | No | **Yes** |
| `ASTNavigation` | `items[*].href` | No | **Yes** |
| `Listing` (Shadowed) | `linkTo` | No | **Yes** |
| `RedirectBlock` | `href` | Yes | Yes |
| `CountryMapObservatory`| `href` | Yes | Yes |
| `CollectionStatistics` | `href` | Yes | Yes |

## Recommendations for Future Blocks
When developing new Volto blocks for Climate-ADAPT:
1.  **Naming**: Prefer standard field names (`url`, `href`, `preview_image`) at the top level when possible.
2.  **Nesting**: If links must be nested in a list, ensure they are inside an `items` list and use `source`, `href`, or `url` as the property name to benefit from this retriever.
3.  **UIDs**: Always store internal links in the `resolveuid/<UID>` format.
