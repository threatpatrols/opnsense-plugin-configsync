"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification,
    are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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
