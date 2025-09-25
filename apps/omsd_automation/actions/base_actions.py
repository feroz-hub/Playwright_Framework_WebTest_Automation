import logging

from utils.logger_utils import setup_test_logger


class BaseActions:
    def __init__(self,logger: logging.Logger = None ):
        class_name = self.__class__.__name__
        self.logger = logger or setup_test_logger(class_name)