"""A data manager to be used to process ArcGIS synchronization handlers

This is a replacement for the RabbitMQ integration. It allows scheduling the
event handlers to be executed at the transaction commit, to ensure data
integrity.
"""

import logging

import transaction

logger = logging.getLogger("eea.climateadat.rabbitmq")


class CallbacksDataManager(object):
    """Transaction aware data manager for calling callbacks at commit time"""

    def __init__(self):
        self.sp = 0
        self.callbacks = []
        self.txn = None

    def tpc_begin(self, txn):
        self.txn = txn

    def tpc_finish(self, txn):
        self.callbacks = []

    def tpc_vote(self, txn):
        pass

    def tpc_abort(self, txn):
        self._checkTransaction(txn)

        if self.txn is not None:
            self.txn = None

        self.callbacks = []

    def abort(self, txn):
        self.callbacks = []

    def commit(self, txn):
        self._checkTransaction(txn)

        for callback in self.callbacks:
            try:
                callback()
            except Exception:
                logger.exception("Error executing callback.")

        self.txn = None
        self.callbacks = []

    def savepoint(self):
        self.sp += 1

        return Savepoint(self)

    def sortKey(self):
        return self.__class__.__name__

    def add(self, callback):
        logger.info("Add callback to queue %s", callback)
        self.callbacks.append(callback)

    def _checkTransaction(self, txn):
        if txn is not self.txn and self.txn is not None:
            raise TypeError("Transaction missmatch", txn, self.txn)


class Savepoint(object):
    """Savepoint implementation to allow rollback of queued callbacks"""

    def __init__(self, dm):
        self.dm = dm
        self.sp = dm.sp
        self.callbacks = dm.callbacks[:]
        self.txn = dm.txn

    def rollback(self):
        if self.txn is not self.dm.txn:
            raise TypeError("Attempt to rollback stale rollback")

        if self.dm.sp < self.sp:
            raise TypeError(
                "Attempt to roll back to invalid save point", self.sp, self.dm.sp
            )
        self.dm.sp = self.sp
        self.dm.callbacks = self.callbacks[:]


def queue_callback(callback):
    cdm = CallbacksDataManager()
    transaction.get().join(cdm)
    cdm.add(callback)
