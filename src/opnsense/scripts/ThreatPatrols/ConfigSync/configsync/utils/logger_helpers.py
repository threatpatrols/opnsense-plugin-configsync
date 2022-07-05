"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
"""

import logging
import logging.handlers
import platform

from configsync.exceptions import ConfigSyncException
from configsync.vars import __title__

CONSOLE_LOGGING_FORMAT = "%(asctime)s %(name)s[%(process)d] %(levelname)s: %(message)s"
SYSLOG_LOGGING_FORMAT = "%(name)s[%(process)d] %(levelname)s: %(message)s"
LOGFILE_LOGGING_FORMAT = "%(asctime)s __hostname__ %(name)s[%(process)d] %(levelname)s: %(message)s"
LOGGING_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


logger = logging.getLogger(__title__)


def init_logger(console_level=None, syslog_level=None, logfile_level=None, logfile_filepath=None):

    # remove any existing handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)

    console_level = __init_console_handler(console_level)
    syslog_level = __init_syslog_handler(syslog_level)
    logfile_level = __init_logfile_handler(logfile_level, logfile_filepath)

    # set the minimum log level
    logger.setLevel(level=min(console_level, syslog_level, logfile_level))


def __init_console_handler(console_level):

    if not console_level:
        return 100

    log_level = logging.getLevelName(console_level.upper())
    try:
        int(log_level)
    except ValueError:
        raise ConfigSyncException(f"Unknown console_level:{console_level} requested")

    logging_format = logging.Formatter(
        fmt=CONSOLE_LOGGING_FORMAT.replace("__hostname__", str(platform.node()).split(".")[0]),
        datefmt=LOGGING_DATE_FORMAT,
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging_format)
    logger.addHandler(console_handler)

    return log_level


def __init_syslog_handler(syslog_level):

    if not syslog_level:
        return 100

    log_level = logging.getLevelName(syslog_level.upper())
    try:
        int(log_level)
    except ValueError:
        raise ConfigSyncException(f"Unknown syslog_level:{syslog_level} requested")

    logging_format = logging.Formatter(
        fmt=SYSLOG_LOGGING_FORMAT.replace("__hostname__", str(platform.node()).split(".")[0]),
        datefmt=LOGGING_DATE_FORMAT,
    )

    if platform.system().lower().endswith("bsd"):
        syslog_address = "/var/run/log"
    else:
        syslog_address = "/dev/log"

    syslog_handler = logging.handlers.SysLogHandler(address=syslog_address)
    syslog_handler.setLevel(log_level)
    syslog_handler.setFormatter(logging_format)
    logger.addHandler(syslog_handler)

    return log_level


def __init_logfile_handler(logfile_level, logfile_filepath):

    if not logfile_level or not logfile_filepath:
        return 100

    log_level = logging.getLevelName(logfile_level.upper())
    try:
        int(log_level)
    except ValueError:
        raise ConfigSyncException(f"Unknown logfile_level:{logfile_level} requested")

    logging_format = logging.Formatter(
        fmt=LOGFILE_LOGGING_FORMAT.replace("__hostname__", str(platform.node()).split(".")[0]),
        datefmt=LOGGING_DATE_FORMAT,
    )

    try:
        file_handler = logging.FileHandler(filename=logfile_filepath)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging_format)
        logger.addHandler(file_handler)
    except Exception:
        logger.warning(f"Unable to write to logfile at: {logfile_filepath}")

    return log_level
