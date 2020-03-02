import sys
import logging
from logging.handlers import RotatingFileHandler
from c42eventextractor.logging.formatters import (
    FileEventDictToJSONFormatter,
    FileEventDictToCEFFormatter,
    FileEventDictToRawJSONFormatter,
)
from c42eventextractor.logging.handlers import NoPrioritySysLogHandlerWrapper

from code42cli.compat import str
from code42cli.securitydata.options import OutputFormat
from code42cli.util import get_user_project_path, print_error


def get_logger_for_stdout(output_format):
    logger = logging.getLogger("code42_stdout_{0}".format(output_format.lower()))
    if _logger_has_handlers(logger):
        return logger

    handler = logging.StreamHandler(sys.stdout)
    return _init_logger(logger, handler, output_format)


def get_logger_for_file(filename, output_format):
    logger = logging.getLogger("code42_file_{0}".format(output_format.lower()))
    if _logger_has_handlers(logger):
        return logger

    handler = logging.FileHandler(filename, delay=True)
    return _init_logger(logger, handler, output_format)


def get_logger_for_server(hostname, protocol, output_format):
    logger = logging.getLogger("code42_syslog_{0}".format(output_format.lower()))
    if _logger_has_handlers(logger):
        return logger

    handler = NoPrioritySysLogHandlerWrapper(hostname, protocol=protocol).handler
    return _init_logger(logger, handler, output_format)


def get_error_logger():
    log_path = get_user_project_path("log")
    log_path = "{0}/code42_errors.log".format(log_path)
    logger = logging.getLogger("code42_error_logger")
    if _logger_has_handlers(logger):
        return logger

    formatter = logging.Formatter("%(asctime)s %(message)s")
    handler = RotatingFileHandler(log_path, maxBytes=250000000)
    return _apply_logger_dependencies(logger, handler, formatter)


def _logger_has_handlers(logger):
    return len(logger.handlers)


def _init_logger(logger, handler, output_format):
    formatter = _get_formatter(output_format)
    logger.setLevel(logging.INFO)
    return _apply_logger_dependencies(logger, handler, formatter)


def _apply_logger_dependencies(logger, handler, formatter):
    try:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except Exception as ex:
        print_error(str(ex))
        exit(1)
    return logger


def _get_formatter(output_format):
    if output_format == OutputFormat.JSON:
        return FileEventDictToJSONFormatter()
    elif output_format == OutputFormat.CEF:
        return FileEventDictToCEFFormatter()
    else:
        return FileEventDictToRawJSONFormatter()