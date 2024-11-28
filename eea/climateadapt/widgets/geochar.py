from zope.component.hooks import getSite
import Acquisition
import z3c.form.browser.textarea
import z3c.form.interfaces
import z3c.form.widget
import zope
import zope.interface
import zope.schema.interfaces
from zope.interface import implementer

class IGeoCharWidget(z3c.form.interfaces.ITextAreaWidget):
    pass


@implementer(IGeoCharWidget)
class GeoCharWidget(z3c.form.browser.textarea.TextAreaWidget):
    klass = 'geochar-widget'
    value = ''

    def update(self):
        super(z3c.form.browser.textarea.TextAreaWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)
        # We'll wrap context in the current site *if* it's not already
        # wrapped.  This allows the template to acquire tools with
        # ``context/portal_this`` if context is not wrapped already.
        # Any attempts to satisfy the Kupu template in a less idiotic
        # way failed:
        if getattr(self.form.context, 'aq_inner', None) is None:
            self.form.context = Acquisition.ImplicitAcquisitionWrapper(
                self.form.context, getSite())


@zope.component.adapter(zope.schema.interfaces.IField,
                        z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def GeoCharFieldWidget(field, request):
    """IFieldWidget factory for WysiwygWidget."""
    return z3c.form.widget.FieldWidget(field, GeoCharWidget(request))
