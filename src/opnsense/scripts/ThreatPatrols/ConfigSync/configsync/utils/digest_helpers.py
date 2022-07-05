"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
"""

import base64
import hashlib
import logging

from configsync.vars import __title__
from configsync.vars import __configsync_digest_method__


logger = logging.getLogger(__title__)


def content_digest(content: bytes, digest_type="hexdigest") -> str:
    """
    Computes the hash digest of the supplied content and returns the hex-digest value

    :param content:
    :param digest_type:
    :return:
    """
    logger.debug(f"content_digest(<content>, digest_type={digest_type})")

    digest = hashlib.new(__configsync_digest_method__.lower())
    digest.update(content)

    if digest_type == "base64":
        return base64.b64encode(digest.digest()).decode()
    return digest.hexdigest()


def file_digest(filename: str, buffer_size=4096) -> str:
    """
    Computes the hash digest of a file and returns the hex-digest value

    :param filename:
    :param buffer_size:
    :return:
    """
    logger.debug(f"file_digest(filename={filename}, buffer_size={buffer_size})")

    digest = hashlib.new(__configsync_digest_method__.lower())
    with open(filename, "rb") as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            digest.update(data)
    return digest.hexdigest()
