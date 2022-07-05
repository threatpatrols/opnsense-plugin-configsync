"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
"""

import os
import time
import shutil
import logging
import subprocess
from typing import Tuple

from configsync.exceptions import ConfigSyncException
from configsync.vars import __title__
from configsync.vars import __system_sync_bin__
from configsync.vars import __configsync_read_consistent_min_max__

from .digest_helpers import file_digest
from .random_helpers import random_chars
from .random_helpers import random_float


logger = logging.getLogger(__title__)


def read_consistent(filename: str, __attempt=1, __max_attempts=16) -> bytes:
    """
    Reads a file twice with a short (random) delay in-between then compares each to confirm they are consistent
    for the purpose of guarding against situations where the file is simultaneously being written to.

    :param filename:
    :param __attempt:
    :param __max_attempts:
    :return:
    """
    logger.debug(f"read_consistent(filename={filename}, __attempt={__attempt}, __max_attempts={__max_attempts})")

    if __attempt >= __max_attempts:
        raise ConfigSyncException("Too many retries while attempting to call read_consistent()", filename)

    randomchars = random_chars()
    tempfile_0 = f"/tmp/read_consistent.0.{randomchars}"
    tempfile_1 = f"/tmp/read_consistent.1.{randomchars}"

    subprocess.call([__system_sync_bin__])
    shutil.copy(filename, tempfile_0)
    digest_0 = file_digest(tempfile_0)

    sleep_minimum, sleep_maximum = __configsync_read_consistent_min_max__
    time.sleep(random_float(minimum_value=sleep_minimum, maximum_value=sleep_maximum))

    subprocess.call([__system_sync_bin__])
    shutil.copy(filename, tempfile_1)
    digest_1 = file_digest(tempfile_1)

    if digest_0 != digest_1:
        os.unlink(tempfile_0)
        os.unlink(tempfile_1)
        return read_consistent(filename, __attempt=__attempt + 1)

    with open(tempfile_0, "rb") as f:
        content = f.read()

    os.unlink(tempfile_0)
    os.unlink(tempfile_1)

    return content


def file_metadata(filename: str, digest_value=False) -> Tuple[dict, None]:
    """
    Collects metadata about the supplied filename

    :param filename:
    :param digest_value:
    :return:
    """
    logger.debug(f"file_metadata(filename={filename}, digest_value={digest_value})")

    if not os.path.isfile(filename):
        return None

    metadata = {
        "bytes": os.path.getsize(filename),
        "ctime": os.path.getctime(filename),
        "mtime": os.path.getmtime(filename),
        "atime": os.path.getatime(filename),
    }

    if digest_value:
        metadata["digest"] = file_digest(filename)
    return metadata
