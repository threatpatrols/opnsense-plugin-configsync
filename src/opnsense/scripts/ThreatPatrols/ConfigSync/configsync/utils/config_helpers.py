"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
"""

import os
import logging
import configparser
from typing import Tuple

from configsync.exceptions import ConfigSyncException
from configsync.vars import __title__


logger = logging.getLogger(__title__)


def read_configfile(filename: str, section: str) -> Tuple[dict, None]:
    """
    Loads a .ini format config file using configparser and returns the section-name required as a dict

    :param filename:
    :param section:
    :return:
    """
    logger.debug(f"read_configfile(filename={filename}, section={section})")

    if not os.path.isfile(filename):
        raise ConfigSyncException("Unable to locate configuration file", filename)

    config = configparser.ConfigParser()
    config.read(filename)

    if section not in config.sections():
        return None

    configuration = {}
    for option, value in config.items(section):
        configuration[str(option).lower()] = value

    return configuration
