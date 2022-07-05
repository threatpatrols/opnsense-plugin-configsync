import os
import sys

try:
    from configsync.exceptions import ConfigSyncException
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from configsync.exceptions import ConfigSyncException

from configsync.utils.random_helpers import random_chars
from configsync.utils.random_helpers import random_float


def test_random_chars():

    response = random_chars(length=30)
    assert len(response) == 30

    response = random_chars()
    assert len(response) == 8


def test_random_float():

    response = random_float(minimum_value=0.1, maximum_value=0.9)
    assert response >= 0.1
    assert response <= 0.9
