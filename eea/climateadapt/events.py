from plone.app.contentrules.handlers import execute_rules
from plone.app.iterate.dexterity.utils import get_baseline
from plone.app.iterate.event import WorkingCopyDeletedEvent
from zope.event import notify


def trigger_contentrules(event):
    execute_rules(event)


def handle_iterate_wc_deletion(object, event):
    """ When a WorkingCopy is deleted, the problem was that the locking was not
    removed. We're manually triggering the IWorkingCopyDeletedEvent because
    the plone.app.iterate handler is registered for IWorkingCopyRelation, a
    derivate of Archetype's relations, which is not used in the dexterity
    implementation.
    """
    try:
        baseline = get_baseline(object)
    except:
        return
    notify(WorkingCopyDeletedEvent(object, baseline, relation=None) )
