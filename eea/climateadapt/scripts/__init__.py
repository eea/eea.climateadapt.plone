"""Script utilities"""

from zope.interface import alsoProvides
from eea.climateadapt.interfaces import IEEAClimateAdaptInstalled

HOST = "climate-adapt.eea.europa.eu"
PLONE = "/cca"


def get_plone_site(zope_conf="/app/etc/relstorage.conf", portal_id="cca"):
    import os
    import Zope2
    from Testing.makerequest import makerequest
    from Zope2.Startup.run import make_wsgi_app
    from zope.component.hooks import setSite
    from zope.globalrequest import setRequest
    from AccessControl.SpecialUsers import system as user
    from AccessControl.SecurityManagement import newSecurityManager

    if getattr(Zope2, "bobo_application", None) is None:
        if zope_conf and os.path.exists(zope_conf):
            make_wsgi_app({}, zope_conf)
        else:
            raise RuntimeError(
                f"Zope not initialized and zope_conf '{zope_conf}' not found."
            )

    app = Zope2.app()

    app = makerequest(app)
    app.REQUEST["PARENTS"] = [app]
    path = [portal_id] if isinstance(portal_id, str) else list(portal_id)
    app.REQUEST.other["VirtualRootPhysicalPath"] = path

    alsoProvides(app.REQUEST, IEEAClimateAdaptInstalled)
    setRequest(app.REQUEST)

    newSecurityManager(None, user)

    site = app[path[-1]]
    setSite(site)

    return site
