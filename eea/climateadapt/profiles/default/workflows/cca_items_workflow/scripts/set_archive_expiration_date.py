## Script (Python) "set_archive_expiration_date"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=change
##title=Set the expiration date
##
obj = change.object
obj.setExpirationDate(obj.modified())
