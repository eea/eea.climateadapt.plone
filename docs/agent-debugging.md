# Agent Debugging Guide

This guide explains how AI agents and developers can connect to the live Plone/Zope database (ZODB) to run diagnostics, scripts, and debug database objects.

## Executing Scripts Inline

In this repository, the Plone backend container runs with a ZODB stored in PostgreSQL via RelStorage. To run a Python script against the live database without having to write/copy files into the running container, you can pass the script code through standard input (`stdin`) using `docker compose exec -T`.

### The Command Pattern

```bash
cat path/to/script.py | \
  docker compose exec -T backend /app/docker-entrypoint.sh /app/bin/python3 - \
  --portal cca \
  --zope-conf /app/etc/relstorage.conf
```

### Why this works:

1. **`-T` flag**: The `-T` option in `docker compose exec` disables pseudo-TTY allocation. This allows you to redirect the file contents from the host's standard input into the container.
2. **`docker-entrypoint.sh` wrapper**: The script `/app/docker-entrypoint.sh` must be used as a wrapper. It exports crucial environment variables (e.g., `SECURITY_POLICY_IMPLEMENTATION=C`) that the Zope WSGI app/ZConfig schema parser needs to boot. Running `/app/bin/python3` directly will fail with a `SubstitutionReplacementError`.
3. **Python `-` argument**: The `-` tells the Python interpreter to read code from stdin. Any arguments following `-` are passed to the script's `sys.argv`.
4. **RelStorage config**: Use `/app/etc/relstorage.conf` (not `zope.conf`) as the configuration file since Plone uses RelStorage to connect to the PostgreSQL database in the development stack.
5. **Working directory**: Run these commands from the `backend/` directory so that `docker compose` picks up the correct compose file. Alternatively, use `docker compose -f /path/to/backend/docker-compose.yml`.

---

## Inline Code Execution Examples

Run these commands from the `backend/` directory on the host:

### 1. Simple ZODB Connection Check
List the root database keys:

```bash
docker compose exec -T backend /app/docker-entrypoint.sh /app/bin/python3 - << 'EOF'
import Zope2
from Zope2.Startup.run import make_wsgi_app
make_wsgi_app({}, "/app/etc/relstorage.conf")
app = Zope2.app()
print("Root keys:", app.keys())
EOF
```

Expected output:
```
Root keys: ['browser_id_manager', 'session_data_manager', 'error_log', 'virtual_hosting', 'index_html', 'cca', 'acl_users']
```

### 2. Introspecting Plone Objects
Bootstrap the Plone site context using the `get_plone_site()` helper:

```bash
docker compose exec -T backend /app/docker-entrypoint.sh /app/bin/python3 - << 'EOF'
from eea.climateadapt.scripts import get_plone_site
site = get_plone_site()
print("Site ID:", site.getId())
print("Available languages:", site.keys())
EOF
```

### 3. Full App Bootstrap (for scripts that need request context)

Some scripts need the full Zope request machinery (hooks, security manager, request object). Use this pattern:

```bash
docker compose exec -T backend /app/docker-entrypoint.sh /app/bin/python3 - << 'PYEOF'
import sys
sys.argv = ["my_script"]

# Bootstrap Zope app
from Zope2.Startup.run import make_wsgi_app
make_wsgi_app({}, "/app/etc/relstorage.conf")

import Zope2
from Testing.makerequest import makerequest
from zope.component.hooks import setSite
from zope.globalrequest import setRequest
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.users import system as system_user

app = Zope2.app()
app = makerequest(app)
app.REQUEST["PARENTS"] = [app]
setRequest(app.REQUEST)
newSecurityManager(None, system_user)

# Now you have full Plone context
portal = app["cca"]
setSite(portal)

# Your investigation code here
from plone import api
brains = api.content.find(portal_type="Document")
print(f"Found {len(brains)} documents")
PYEOF
```

---

## Troubleshooting

### `SubstitutionReplacementError: no replacement for 'SECURITY_POLICY_IMPLEMENTATION'`

This means you are running Python directly without the `docker-entrypoint.sh` wrapper. The entrypoint sets all the environment variables that `relstorage.conf` expects. Always use:

```bash
docker compose exec -T backend /app/docker-entrypoint.sh /app/bin/python3 - << 'EOF'
...
EOF
```

### `ZConfig.DataConversionError: /app/lib/python3.12/var is not an existing directory`

The `relstorage.conf` references `$INSTANCE/var` paths. If you are running outside the entrypoint (e.g., with `docker exec`), create the directory first:

```bash
docker exec backend-backend-1 mkdir -p /app/lib/python3.12/var
```

### `Error resolving behavior ... for factory ...`

These `ERROR:plone.dexterity.schema` messages are harmless. They appear because the standalone bootstrap doesn't have a full HTTP request context (no `ISiteRoot` traversal). The scripts still work correctly.

### `plone.app.theming pkg_resources is deprecated`

Harmless warning from `setuptools`. Can be ignored.

### Running from outside the `backend/` directory

If you are not in the `backend/` directory, specify the compose file explicitly:

```bash
docker compose -f backend/docker-compose.yml exec -T backend /app/docker-entrypoint.sh /app/bin/python3 - << 'EOF'
...
EOF
```

Or use the container name directly (as shown in the "Full App Bootstrap" pattern above) with `docker exec` — but note you must then set environment variables manually.

### Container name

The backend container is named `backend-backend-1` (from the root-level `docker-compose.yml` stack) or can be referenced as `backend` via `docker compose exec` from the `backend/` directory.

---

## Quick Reference: Bootstrap Patterns

### Minimal (ZODB access only — no Plone hooks)

```python
from Zope2.Startup.run import make_wsgi_app
make_wsgi_app({}, "/app/etc/relstorage.conf")
import Zope2
app = Zope2.app()
site = app["cca"]
```

### Full (with request, security, and site hooks)

```python
from Zope2.Startup.run import make_wsgi_app
make_wsgi_app({}, "/app/etc/relstorage.conf")

import Zope2
from Testing.makerequest import makerequest
from zope.component.hooks import setSite
from zope.globalrequest import setRequest
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.users import system as system_user

app = Zope2.app()
app = makerequest(app)
app.REQUEST["PARENTS"] = [app]
setRequest(app.REQUEST)
newSecurityManager(None, system_user)

portal = app["cca"]
setSite(portal)
```

### Using the project helper

```python
from eea.climateadapt.scripts import get_plone_site
site = get_plone_site()
```

This calls `Zope2.app()` internally and sets up request hooks. Works when the Zope app is already bootstrapped by `make_wsgi_app` or `zconsole run`.
