from . import monitoritem
from . import intervalitem


class MonitorItemFactory:

    @classmethod
    def create_item(cls, host, pvname, item_key=None):
        return monitoritem.MonitorItem(host, pvname, item_key)


class IntervalItemFactory:
    DEFAULT_FUNCTION = 'last'

    _functions = {'last': intervalitem.IntervalItemHasLast,
                  'min': intervalitem.IntervalItemHasMin,
                  'max': intervalitem.IntervalItemHasMax,
                  'avg': intervalitem.IntervalItemHasAvg}

    @classmethod
    def create_item(cls, host, pvname, interval=None,
                    func=None, item_key=None):
        if (func not in cls._functions):
            # Set default function
            func = cls.DEFAULT_FUNCTION

        item_class = cls._functions[func]
        return item_class(host, pvname, interval, item_key)

    @classmethod
    def list_of_functions(cls):
        return cls._functions
