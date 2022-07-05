import os
import sys
import subprocess

try:
    from configsync.exceptions import ConfigSyncException
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from configsync.exceptions import ConfigSyncException

from configsync.utils.digest_helpers import file_digest
from configsync.utils.digest_helpers import content_digest
from configsync.utils.random_helpers import random_chars


def test_content_digest01():

    content = "dG4oQtEZsZibWOuQmmLl".encode("utf8")
    response = content_digest(content)

    assert response == "181c172bf2ec5d418e6b5f2925c1e029"


def test_content_digest02():

    content = b"dG4oQtEZsZibWOuQmmLl"
    response = content_digest(content)

    assert response == "181c172bf2ec5d418e6b5f2925c1e029"


def test_content_digest03():

    content = b"dG4oQtEZsZibWOuQmmLl"
    response = content_digest(content, digest_type="base64")

    assert response == "GBwXK/LsXUGOa18pJcHgKQ=="


def test_file_digest01():

    content = random_chars(length=32000).encode("utf8")
    contentdigest = content_digest(content)

    filename = f"/tmp/configsync_test_{random_chars()}.random"
    with open(filename, "wb") as f:
        f.write(content)

    filedigest = file_digest(filename=filename, buffer_size=256)

    assert contentdigest == filedigest
    os.unlink(filename)
