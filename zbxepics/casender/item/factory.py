from . import monitoritem
from . import intervalitem


class MonitorItemFactory:
    """Factory for creating monitor item"""

    @classmethod
    def create_item(cls, host, pvname, item_key=None):
        """Create monitor item

        Returns
        -------
        item.MonitorItem
            created item
        """

        return monitoritem.MonitorItem(host, pvname, item_key)


class IntervalItemFactory:
    """Factory for creating interval item"""

    DEFAULT_FUNCTION = 'last'

    _functions = {'last': intervalitem.IntervalItemHasLast,
                  'min': intervalitem.IntervalItemHasMin,
                  'max': intervalitem.IntervalItemHasMax,
                  'avg': intervalitem.IntervalItemHasAvg}

    @classmethod
    def create_item(cls, host, pvname, interval=None,
                    func=None, item_key=None):
        """Create interval item

        Parameters
        ----------
        host : str
            host name of item
        pvname : str
            pv name to monitor
        interval : int
            interval in senconds to send
        func : str
            function to apply item buffer
        item_key : str
            item key of item

        Returns
        -------
        item.IntervalItem
            created item
        """

        if (func not in cls._functions):
            # Set default function
            func = cls.DEFAULT_FUNCTION

        item_class = cls._functions[func]
        return item_class(host, pvname, interval, item_key)

    @classmethod
    def list_of_functions(cls):
        """get a list of functions

        Returns
        -------
        list
            list of functions
        """

        return cls._functions
