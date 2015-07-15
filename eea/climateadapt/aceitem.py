from eea.climateadapt import MessageFactory as _
from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable
from zope.interface import implements
from zope.schema import Choice

#from five import grok
# from zope import schema
# from zope.schema.interfaces import IContextSourceBinder
# from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
#
# from zope.interface import invariant, Invalid, implements
#
# from z3c.form import group, field
#
# from plone.namedfile.field import NamedImage, NamedFile
# from plone.namedfile.field import NamedBlobImage, NamedBlobFile
#
# from plone.app.textfield import RichText
#
# from z3c.relationfield.schema import RelationList, RelationChoice
# from plone.formwidget.contenttree import ObjPathSourceBinder
#
#

# Interface class; used to define content-type schema.

class IAceItem(form.Schema, IImageScaleTraversable):
    """
    Generic Ace Item
    """

    # form.model("models/aceitem.xml")

    data_type = Choice(title=_(u"Data Type"),
                       required=True,
                       vocabulary="eea.climateadapt.aceitems_datatypes")

    storage_type = Choice(title=_(u"Storage Type"),
                       required=True,
                       vocabulary="eea.climateadapt.aceitems_storagetypes")

class AceItem(dexterity.Item):
    implements(IAceItem)

    # TODO: special search behaviour, should aggregate most fields
    # TODO: "keyword" from SQL is Subject

