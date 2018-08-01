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

    _functions = {'last': intervalitem.IntervalItemLast,
                  'min': intervalitem.IntervalItemMin,
                  'max': intervalitem.IntervalItemMax,
                  'avg': intervalitem.IntervalItemAvg}

    @classmethod
    def create_item(cls, host, pvname, interval=30.0,
                    func='last', item_key=None):
        """Create interval item

        Parameters
        ----------
        host : str
            host name of item
        pvname : str
            pv name to monitor
        interval : float
            interval in senconds to send  (default is 30)
        func : str
            function to apply item buffer (default is 'last')
        item_key : str
            item key of item (default is None)

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
