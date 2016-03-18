from eea.climateadapt.mayorsadapt.roleplugin import is_citymayor_visitor
from plone.api.content import get_state
from plone.app.layout.viewlets import ViewletBase
from plone.app.stagingbehavior.utils import get_baseline
from plone.app.stagingbehavior.utils import get_working_copy


class EditMenuViewlet(ViewletBase):
    """ Viewlet that implements the editing interface for the city profile
    """

    def state_labels(self):
        return {
            'private': 'Private',
            'published': 'Published',
            'pending': 'Pending aproval',
        }

    def render(self):
        print "WC: ", get_working_copy(self.context)
        print "Baseline: ", get_baseline(self.context)

        if not self.available():
            return ""
        return super(EditMenuViewlet, self).render()

    def available(self):
        return is_citymayor_visitor(self.request)

    def current_state(self):
        return get_state(self.context)

    def can_submit_for_publication(self):
        # TODO: return True if transition submit is available
        return self.current_state() == 'private'

    def has_working_copy(self):
        return get_working_copy(self.context) is not None
