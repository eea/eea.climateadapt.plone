from plone.app.event.browser.event_view import EventView
import datetime

class CcaEvent(EventView):

    def future_event(self):
        #import pdb; pdb.set_trace()
        if self.context.online_registration and self.context.start.strftime('%Y-%m-%d') > datetime.datetime.now().strftime('%Y-%m-%d'):
            return True
        return False
