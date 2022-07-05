"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
"""

import logging
import subprocess

from configsync.vars import __title__
from configsync.exceptions import ConfigSyncException


logger = logging.getLogger(__title__)


def exec_command(command_line: str, timeout=10) -> tuple:
    """
    Execute a shell command and return the stdout, stderr and exit-code

    :param command_line: str
    :param timeout: int
    :return:
    """
    logger.debug(f"exec_command(command_line={command_line}, timeout={timeout})")
    try:
        sp = subprocess.run(command_line, shell=True, capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as e:
        raise ConfigSyncException(e) from e

    logger.debug(
        f"exec_command() -> stdout=<stdout:len={len(sp.stdout)}> "
        f"stderr=<stderr:len={len(sp.stderr)}> returncode={sp.returncode}"
    )
    return sp.stdout, sp.stderr, sp.returncode
