# Instructions to configure LDAP Eionet logging in to the CCA website

1. Install plone.app.ldap profile in Plone / Addons
2. Inside acl_users, create a new LDAP Multi Plugin object named "ldap-roles"
3. Configure as following:

* login name: uid
* user id attribute: uid
* RDN attribute: uid
* Users Base DN: ou=Users,o=EIONET,l=Europe  scope SUBTREE
* Group storage: groups stored on LDAP server
* group mapping: manually map groups to Zope roles
* groups base DN: ou=Roles,o=EIONET,l=Europe scope SUBTREE
* Manager DN: any uid, such as uid=tiberich,ou=Users,o=EIONET,l=Europe
* fill in that user password
* Manager DN Usage: Always
* User object classes: top, person
* User password encryption: SHA
* Default user roles: Authenticated


Map appropriate groups to Zope roles, in the Groups tab, /acl_users/ldap-roles/acl_users/manage_grouprecords

