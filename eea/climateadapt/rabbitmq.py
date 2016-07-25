""" Configuration for RabbitMQ client
"""

from eea.rabbitmq.client import RabbitMQConnector
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.registry.interfaces import IRegistry
from plone.z3cform import layout
from z3c.form import form
from zope.component import getUtility
from zope.interface import Interface
from zope.schema import TextLine, Int


class IRabbitMQClientSettings(Interface):
    """ Client settings for RabbitMQ
    """

    server = TextLine(title=u"Server Address", required=True,
                      default=u"localhost")
    port = Int(title=u"Server port", required=True, default=6527)
    username = TextLine(title=u"Username", required=True)
    password = TextLine(title=u"Password", required=True)


class RabbitMQClientControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = IRabbitMQClientSettings


RabbitMQClientControlPanelView = layout.wrap_form(
    RabbitMQClientControlPanelForm, ControlPanelFormWrapper)
RabbitMQClientControlPanelView.label = u"RabbitMQ Client settings"


RABBIT_QUEUE = 'eea.climateadapt'

def queue_msg(msg, queue=None):
    if queue == None:
        queue = RABBIT_QUEUE

    registry = getUtility(IRegistry)
    s = registry.forInterface(IRabbitMQClientSettings)

    rb = RabbitMQConnector(s.server, s.port, s.username, s.password)
    rb.open_connection()
    rb.declare_queue(queue)
    rb.send_message(queue, msg)
