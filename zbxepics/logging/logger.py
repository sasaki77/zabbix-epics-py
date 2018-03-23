import os
import logging
import logging.config


class Logger(object):

    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    LEVELS = [NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL]

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.debug('Create logger(%s)', self.logger.name)

    def set_config(self, config_file):
        # If value is `True` then default config path will used
        if config_file and isinstance(config_file, bool):
            dir_path = os.path.dirname(__file__)
            config_file = os.path.join(dir_path, 'logging.conf')
        # Set configuration for logging
        logging.config.fileConfig(config_file,
                                  disable_existing_loggers=False)

        self.debug('Changed configuration for logger(%s)', self.logger.name)

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
