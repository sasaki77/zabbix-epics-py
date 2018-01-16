import logging


class Logger(object):

    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    LEVELS = [NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL]

    def __init__(self):
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s',
            '%Y-%m-%d %H:%M:%S')
        stream_handler.setFormatter(formatter)

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(stream_handler)

    def set_level(self, level):
        if level in self.LEVELS:
            self.logger.setLevel(level)

    def debug(self, msg, *args, **kw):
        self.log(self.DEBUG, msg, *args, **kw)

    def info(self, msg, *args, **kw):
        self.log(self.INFO, msg, *args, **kw)

    def warning(self, msg, *args, **kw):
        self.log(self.WARNING, msg, *args, **kw)

    def error(self, msg, *args, **kw):
        self.log(self.ERROR, msg, *args, **kw)

    def critical(self, msg, *args, **kw):
        self.log(self.CRITICAL, msg, *args, **kw)

    def log(self, level, msg, *args, **kw):
        self.logger.log(level, msg, *args, **kw)


logger = Logger()
