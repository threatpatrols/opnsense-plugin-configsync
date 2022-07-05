"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
"""

import os
import logging
import platform

from configsync.vars import __title__
from configsync.vars import __system_hostid_file__


logger = logging.getLogger(__title__)


def get_system_hostid() -> str:
    """
    Reads the system hostid file and returns this value if exists, else returns a dummy zero'd value

    :return:
    """
    logger.debug("get_system_hostid()")

    hostid = "00000000-0000-0000-0000-000000000000"
    if os.path.isfile(__system_hostid_file__):
        with open(__system_hostid_file__, "rb") as f:
            data = f.read()
            if len(data) > 30:
                hostid = data.decode("utf8").strip()
    return hostid


def get_system_hostname() -> str:
    """
    Acquires the system hostname via the Python platform.node() function

    :return:
    """
    logger.debug("get_system_hostname()")

    return str(platform.node()).split(".", maxsplit=1)[0]
