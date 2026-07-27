# Microsoft Entra ID Authentication

## Overview

Climate-ADAPT is migrating from Eionet LDAP authentication to **Microsoft Entra ID** (formerly Azure AD) using OAuth2. This document outlines the technical implementation, plugin configuration, and setup steps for staging and production environments.

The authentication stack is built on top of:

- **[pas.plugins.eea](https://github.com/eea/pas.plugins.eea)** — EEA PAS plugin collection that installs and configures the underlying authentication infrastructure
- **pas.plugins.authomatic** — OAuth2/OAuth1/OpenID authentication plugin for Plone, providing the Microsoft Entra ID provider integration

## Architecture

```
Browser ──► Volto/Plone ──► pas.plugins.authomatic ──► Microsoft Entra ID (OAuth2)
                                      │
                              acl_users (PAS pipeline)
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
            eea_entra (Properties)  User_Enumeration  User_Ader
            (login = email)         (disabled)        (disabled)
```

Users authenticate via the Microsoft Entra ID OAuth2 flow. On successful authentication, `pas.plugins.authomatic` creates or updates the Plone user and maps Entra ID profile attributes to Plone user properties.

## Implementation Steps

### 1. Install Required Packages

Add `pas.plugins.eea` to the buildout dependencies. This package pulls in `pas.plugins.authomatic` and related PAS plugins as dependencies.

```ini
# buildout.cfg / requirements
eggs =
    pas.plugins.eea
    # ... other eggs
```

Re-run buildout to install the packages:

```bash
make install
```

### 2. Configure authomatic for Microsoft Entra ID

Navigate to **Site Setup → Authomatic Configuration** (or `@@authomatic-controlpanel`) and configure the Microsoft provider with the following JSON settings.

> **Secrets**: The `consumer_key` and `consumer_secret` values below are placeholders. Use the actual values from the EEA Azure AD application registration. These should be managed as secrets (environment variables or Ansible vault) and must never be committed to version control.

```json
{
    "microsoft": {
        "id": 1,
        "scope": [
            "User.ReadBasic.All"
        ],
        "domain": "EEA1.onmicrosoft.com",
        "display": {
            "title": "EEA Microsoft Entra ID",
            "cssclasses": {
                "button": "plone-btn plone-btn-default",
                "icon": "glypicon glyphicon-microsoft"
            },
            "as_form": false
        },
        "propertymap": {
            "id": "id",
            "mail": "email",
            "country": "location",
            "name": "fullname"
        },
        "sync_propertymap": {
            "id": "id",
            "mail": "email",
            "country": "location",
            "displayName": "fullname",
            "userPrincipalName": "email",
            "userType": null
        },
        "class_": "authomatic.providers.oauth2.MicrosoftOnline",
        "consumer_key": "<ENTER-CONSUMER-KEY>",
        "consumer_secret": "<ENTER-CONSUMER-SECRET>",
        "access_headers": {
            "User-Agent": "Plone (pas.plugins.authomatic)"
        }
    }
}
```

#### Configuration Notes

| Setting | Purpose |
|---------|---------|
| `domain` | Restricts login to the EEA tenant (`EEA1.onmicrosoft.com`) |
| `scope` | `User.ReadBasic.All` grants read access to basic profile attributes |
| `propertymap` | Maps initial OAuth2 profile fields to Plone user properties on first login |
| `sync_propertymap` | Maps fields that are synced on every subsequent login |
| `userType: null` | The `userType` field from Entra ID is intentionally ignored (not mapped to any Plone property) |

### 3. Configure Plone User ID Generation

In the **authomatic control panel**, set:

- **Generator for Plone User IDs**: `UUID as User Id`

This ensures that Plone user IDs are generated as UUIDs rather than derived from the email address or Entra ID `id` field, avoiding potential conflicts and keeping user IDs stable.

### 4. Adjust PAS Plugin Settings in `acl_users`

After installation, the default PAS plugin pipeline needs to be adjusted to work correctly with Entra ID authentication. The following plugins must be **disabled** (unchecked) in `acl_users`:

#### authomatic plugin — disable:

| Plugin Feature | Reason |
|----------------|--------|
| **User_Enumeration** | Handled by `eea_entra` — user login property is set to the user email |
| **User_Management** | Entra ID users cannot be deleted from within Plone; disabling this removes the delete checkboxes from the user management UI |
| **Properties** | Handled by `eea_entra` properties plugin, which adds the "External" emoji indicator |
| **User_Ader** | Not needed with Entra ID authentication |

#### mutable_properties plugin — disable:

| Plugin Feature | Reason |
|----------------|--------|
| **User_Enumeration** | Handled by `eea_entra` — user login property is set to the user email |

### 5. Configure Properties Plugin Ordering

In **acl_users → Plugins → Properties**, ensure that **eea_entra** is at the **top** of the "Active Plugins" list. This guarantees that the `eea_entra` properties plugin takes precedence when resolving user properties, ensuring the "External" emoji and email-based login are applied correctly.

## Environment-Specific Setup

### Staging

1. Obtain staging-specific Azure AD application credentials (separate from production)
2. Apply the same authomatic JSON configuration with staging credentials
3. Repeat PAS plugin adjustments (Steps 4–5) — these are configuration-level changes that follow the same pattern across environments
4. Verify the OAuth2 redirect URI is registered in the Azure AD application for the staging domain

### Production

1. Use production Azure AD application credentials
2. Apply the same authomatic JSON configuration with production credentials
3. Repeat PAS plugin adjustments (Steps 4–5)
4. Verify the OAuth2 redirect URI is registered in the Azure AD application for the production domain (`https://climate-adapt.eea.europa.eu`)

### Secrets Management

The `consumer_key` and `consumer_secret` values must be managed as secrets. Recommended approaches:

- **Ansible vault**: Store credentials in the `devops/` Ansible configuration and inject them during deployment
- **Environment variables**: If supported by the deployment pipeline, inject via environment variables into the authomatic configuration at runtime

> **Never commit actual credentials to version control.**

## Migration Considerations

### Existing LDAP Users

The existing Eionet LDAP authentication (`Products.LDAPUserFolder`) remains documented in [authentication-setup.md](./authentication-setup.md). During the migration period:

- Existing local role assignments on content continue to work as-is
- LDAP groups (`extranet-cca-*`) and local groups (`local-*`) remain valid for authorization
- The `migrate_eionet_groups` script can still be used to migrate `extranet-*` → `local-*` references

### User Identity Mapping

With Entra ID authentication:
- **Login name**: Set to the user's email address (via `eea_entra`)
- **User ID**: Generated as a UUID (via authomatic UUID generator)
- **Profile sync**: On each login, `mail`, `country`, `displayName` are synced from Entra ID to Plone properties

### Group Membership

Entra ID authentication handles user identity but **does not automatically sync group membership** from Azure AD to Plone groups. Group-based authorization continues to rely on:

- Local Plone groups (created manually or via the `migrate_eionet_groups` script)
- Local role assignments on content folders
- Any existing LDAP group resolution (if LDAP remains active during transition)

## Troubleshooting

### Users cannot log in

- Verify the `consumer_key` and `consumer_secret` match the Azure AD application registration
- Confirm the `domain` matches the tenant (`EEA1.onmicrosoft.com`)
- Check that the redirect URI in Azure AD matches the Plone instance URL
- Review Plone event logs for authomatic errors

### User properties not syncing

- Ensure `eea_entra` is at the top of the Properties plugin order in `acl_users`
- Verify the `sync_propertymap` in the authomatic configuration maps the expected fields
- Check that the OAuth2 `scope` includes `User.ReadBasic.All`

### Delete checkboxes still visible in user management

- Confirm **User_Management** is disabled on the `authomatic` plugin in `acl_users`

## References

- [pas.plugins.eea](https://github.com/eea/pas.plugins.eea) — EEA PAS plugin collection
- [pas.plugins.authomatic](https://github.com/sergiocorreia/pas.plugins.authomatic) — OAuth2/OAuth1 PAS plugin
- [authomatic](https://github.com/authomatic/authomatic) — Underlying OAuth2 library
- [Existing LDAP authentication setup](./authentication-setup.md) — Legacy Eionet LDAP documentation
- [Migrate Eionet Groups](../eea/climateadapt/scripts/MIGRATE_EIONET_GROUPS.md) — Group migration script documentation
