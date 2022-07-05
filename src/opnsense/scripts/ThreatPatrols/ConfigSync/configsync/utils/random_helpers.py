"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
"""

import random
import logging

from configsync.vars import __title__


logger = logging.getLogger(__title__)


def random_float(minimum_value=0.0, maximum_value=1.0, decimal_places=4) -> float:
    """
    Returns a pseudo random float between the min/max and with the required number of decimal places

    :param minimum_value:
    :param maximum_value:
    :param decimal_places:
    :return:
    """
    return round(random.uniform(minimum_value, maximum_value), decimal_places)


def random_chars(length=8) -> str:
    """
    Returns a pseudo random string with lowercase-chars and numbers, with the required length of chars

    :param length:
    :return:
    """
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(random.choice(chars) for _ in range(length))
