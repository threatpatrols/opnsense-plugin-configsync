import os
import sys
import subprocess

try:
    from configsync.exceptions import ConfigSyncException
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from configsync.exceptions import ConfigSyncException

from configsync.utils.system_helpers import get_system_hostid
from configsync.utils.system_helpers import get_system_hostname
from configsync.utils.random_helpers import random_chars


def test_get_system_hostname():

    response = get_system_hostname()
    assert response is not None
    assert len(response) > 1
    assert isinstance(response, str)


def test_get_system_hostid01(monkeypatch):

    filename = "/tmp/configsync_test.hostid"
    monkeypatch.setattr("configsync.vars.__system_hostid_file__", filename)

    faux_hostid = random_chars(length=20)

    with open(filename, "w") as f:
        f.write(faux_hostid)

    hostid = get_system_hostid()
    assert hostid == "00000000-0000-0000-0000-000000000000"  # occurs because length of hostid is not 36

    os.unlink(filename)


def test_get_system_hostid02(monkeypatch):

    filename = "/tmp/configsync_test.hostid"
    monkeypatch.setattr("configsync.utils.system_helpers.__system_hostid_file__", filename)

    faux_hostid = random_chars(length=36)

    with open(filename, "w") as f:
        f.write(faux_hostid)

    hostid = get_system_hostid()
    assert hostid == faux_hostid

    os.unlink(filename)
