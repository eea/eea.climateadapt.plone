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

RABBIT_QUEUE = 'eea.climateadapt'


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


def get_rabbitmq_conn(context=None, queue=None):
    """ Returns a RabbitMQConnector instance
    """

    if queue == None:
        queue = RABBIT_QUEUE

    registry = getUtility(IRegistry)
    s = registry.forInterface(IRabbitMQClientSettings)

    rb = RabbitMQConnector(s.server, s.port, s.username, s.password)
    rb.open_connection()
    rb.declare_queue(queue)

    return rb


def queue_msg(msg, context=None, queue=None):
    """ Queues a rabbitmq message in the given queue

    If no queue is given, the default RABBIT_QUEUE is used
    """

    conn = get_rabbitmq_conn(context=context, queue=queue)
    conn.send_message(queue, msg)


def consume_messages(callback, context=None, queue=None):
    """ Executes the callback on all messages existing in the queue

    # TODO: implement a lockfile mechanism, see
    # http://fasteners.readthedocs.io/en/latest/api/lock.html#decorators
    """

    if queue is None:
        queue = RABBIT_QUEUE

    conn = get_rabbitmq_conn(context=context, queue=queue)
    while not conn.is_queue_empty(queue):
        msg = conn.get_message(queue)
        callback(msg)
        conn.get_channel().basic_ack(msg[0].delivery_tag)
    conn.close_connection()
