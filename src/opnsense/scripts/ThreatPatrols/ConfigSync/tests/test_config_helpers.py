import os
import sys
import textwrap

try:
    from configsync.exceptions import ConfigSyncException
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from configsync.exceptions import ConfigSyncException

from configsync.utils.config_helpers import read_configfile
from configsync.utils.random_helpers import random_chars


def test_read_configfile01():

    config_filename = __create_configfile()
    config = read_configfile(config_filename, section="storage_provider")
    os.unlink(config_filename)

    assert "path" in config.keys()
    assert "sitename/opnsense/fw01" == config["path"]

    assert "enabled" in config.keys()
    assert True is bool(int(config["enabled"]))


def test_read_configfile02():

    config_filename = __create_configfile()
    config = read_configfile(config_filename, section="monitor_daemon")
    os.unlink(config_filename)

    assert "enabled" in config.keys()
    assert False is bool(int(config["enabled"]))


def __create_configfile():
    filename = f"/tmp/configsync_test_{random_chars()}.conf"
    content = textwrap.dedent(
        """

            [storage_provider]
            enabled=1
            
            # define either the provider+bucket -or- the endpoint url here
            provider=aws_s3
            bucket=randombucket
            endpoint=
            
            # the path within the bucket to store files
            path=sitename/opnsense/fw01
            
            # credentials to use with the storage provider
            key_id=xxxxxxxxxxxxxxxxxxxx
            key_secret=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
            
            
            [monitor_daemon]
            enabled=0
            
            # interval between checks for configuration file change
            check_interval_seconds=10
    
    """
    )

    with open(filename, "w") as f:
        f.write(content)

    return filename
