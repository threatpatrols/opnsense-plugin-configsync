import os
import sys
import pytest

try:
    from configsync.exceptions import ConfigSyncException
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from configsync.exceptions import ConfigSyncException

from configsync.utils.exec_helpers import exec_command


def test_exec_with_timeout_exception01():
    command_line = "sleep 3"

    with pytest.raises(ConfigSyncException) as exception_info:
        exec_command(command_line=command_line, timeout=1)

    assert "TimeoutExpired" in str(exception_info)


def test_exec_simple_command():

    command_line = "ls -al"
    stdout, stderr, returncode = exec_command(command_line=command_line)

    assert isinstance(stdout, bytes) is True
    assert isinstance(stderr, bytes) is True
    assert len(stderr) == 0
    assert returncode == 0
