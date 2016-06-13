from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import implementer
from plone.app.widgets.dx import RichTextWidget


#@adapter(getSpecification(IRichText['text']), IWidgetsLayer)
@implementer(IFieldWidget)
def RichTextFieldWidget(field, request):
    return FieldWidget(field, RichTextWidget(request))

