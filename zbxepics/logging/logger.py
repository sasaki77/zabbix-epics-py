import os
import logging
import logging.config


class Logger(object):
    """DocStrings for Logger class."""

    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    LEVELS = [NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL]

    def __init__(self):
        """Initialize the logger."""
        self.logger = logging.getLogger(__name__)

        self.debug('Create logger(%s)', self.logger.name)

    def set_config(self, config_file):
        """Set configuration for logging from config file.

        :type config_file: str or bool
        :param config_file: Path to config file to load settings from.
         If value is `True` then default config path will used.
        """
        # If value is `True` then default config path will used
        if config_file and isinstance(config_file, bool):
            dir_path = os.path.dirname(__file__)
            config_file = os.path.join(dir_path, 'logging.conf')
        # Set configuration for logging
        logging.config.fileConfig(config_file,
                                  disable_existing_loggers=False)

        self.debug('Changed configuration for logger(%s)', self.logger.name)

    def set_level(self, level):
        """Set the logging level of this logger."""
        if level in self.LEVELS:
            self.logger.setLevel(level)

    def debug(self, msg, *args, **kw):
        """Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value.
        """
        self.log(self.DEBUG, msg, *args, **kw)

    def info(self, msg, *args, **kw):
        """Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value.
        """
        self.log(self.INFO, msg, *args, **kw)

    def warning(self, msg, *args, **kw):
        """Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value.
        """
        self.log(self.WARNING, msg, *args, **kw)

    def error(self, msg, *args, **kw):
        """Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value.
        """
        self.log(self.ERROR, msg, *args, **kw)

    def critical(self, msg, *args, **kw):
        """Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value.
        """
        self.log(self.CRITICAL, msg, *args, **kw)

    def log(self, level, msg, *args, **kw):
        """Log 'msg % args' with the integer severity 'level'.

        To pass exception information, use the keyword argument exc_info with
        a true value.
        """
        self.logger.log(level, msg, *args, **kw)


logger = Logger()
