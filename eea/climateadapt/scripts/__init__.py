""" Script utilities
"""


def get_plone_site():
    import Zope2
    app = Zope2.app()
    from Testing.ZopeTestCase import utils
    utils._Z2HOST = 'climate-adapt.eea.europa.eu'

    app = utils.makerequest(app)
    app.REQUEST['PARENTS'] = [app]
    app.REQUEST.other['VirtualRootPhysicalPath'] = ('', 'cca',)
    from zope.globalrequest import setRequest
    setRequest(app.REQUEST)

    from AccessControl.SpecialUsers import system as user
    from AccessControl.SecurityManagement import newSecurityManager
    newSecurityManager(None, user)

    _site = app['cca']  # NOTICE: hardcoded site name
    site = _site.__of__(app)

    from zope.site.hooks import setSite
    setSite(site)

    return site
