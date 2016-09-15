""" Script utilities
"""

HOST = 'climate-adapt.eea.europa.eu'
PLONE = "/cca"


def get_plone_site():
    import Zope2
    app = Zope2.app()
    from Testing.ZopeTestCase import utils
    utils._Z2HOST = HOST

    path = PLONE.split('/')

    app = utils.makerequest(app)
    app.REQUEST['PARENTS'] = [app]
    app.REQUEST.other['VirtualRootPhysicalPath'] = path
    from zope.globalrequest import setRequest
    setRequest(app.REQUEST)

    from AccessControl.SpecialUsers import system as user
    from AccessControl.SecurityManagement import newSecurityManager
    newSecurityManager(None, user)

    _site = app[path[-1]]
    site = _site.__of__(app)

    from zope.site.hooks import setSite
    setSite(site)

    return site
