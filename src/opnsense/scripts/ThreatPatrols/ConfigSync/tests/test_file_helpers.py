import os
import sys
import textwrap

try:
    from configsync.exceptions import ConfigSyncException
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from configsync.exceptions import ConfigSyncException

from configsync.utils.file_helpers import read_consistent
from configsync.utils.file_helpers import file_metadata
from configsync.utils.digest_helpers import content_digest
from configsync.utils.random_helpers import random_chars


def test_read_consistent01():

    filename = __create_configfile()

    data = read_consistent(filename=filename)
    os.unlink(filename)

    hash_digest = content_digest(data)
    assert hash_digest == "fe366a7ff0df55cf7de83b57bc7c3c1b"


def test_file_metadata01():
    filename = __create_configfile()

    data = file_metadata(filename=filename)
    os.unlink(filename)

    assert data["bytes"] == 757
    assert data["ctime"] == data["mtime"]


def test_file_metadata02():
    filename = __create_configfile()

    data = file_metadata(filename=filename, digest_value=True)
    os.unlink(filename)

    assert data["digest"] == "fe366a7ff0df55cf7de83b57bc7c3c1b"


def __create_configfile():
    filename = f"/tmp/configsync_test_{random_chars()}.conf"
    content = textwrap.dedent(
        """

            [storage_provider]
            enabled=1

            # define either the provider+bucket -or- the endpoint_url here
            provider=aws_s3
            bucket=randombucket
            endpoint_url=

            # the path within the bucket to store files
            path_prefix=sitename/opnsense/fw01

            # credentials to use with the storage provider
            key_id=xxxxxxxxxxxxxxxxxxxx
            key_secret=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


            [monitor_daemon]
            enabled=1

            # interval between checks for configuration file change
            check_interval_seconds=10

            # action to sync the current system config (.xml) file
            pattern_0=/conf/config.xml
            action_0=configctl configsync sync_current_system_config

            # action to sync all system config (.xml) files in the backup path
            pattern_1=/conf/backup/*.xml
            action_1=configctl configsync sync_all_system_configs

    """
    )

    with open(filename, "w") as f:
        f.write(content)
    return filename
