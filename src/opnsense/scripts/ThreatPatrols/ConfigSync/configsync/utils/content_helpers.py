"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
"""

import re
import gzip
import logging
import datetime
from io import BytesIO
import pytz
from typing import Tuple

from configsync.exceptions import ConfigSyncException
from configsync.vars import __title__


logger = logging.getLogger(__title__)


def gzip_content(content: Tuple[str, bytes]) -> bytes:
    """
    Gzips content in a way that is compatible with the system-gzip command, returns gzip file content

    :param content:
    :return:
    """
    logger.debug("gzip_content(<content>)")

    out = BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb") as f:
        if isinstance(content, str):
            f.write(content.encode("utf8"))
        else:
            f.write(content)
    return out.getvalue()


def normalize_timestamp(timestring: Tuple[str, int, float], target_timezone=None) -> str:
    """
    Takes the supplied timestring and normalizes it into format %Y-%m-%d %H:%M:%S optionally
    adjusted into the requested target_timezone

    NB: Handles a limited set of possible input timestring formats only.

    :param timestring:
    :param target_timezone:
    :return:
    """

    def datetime_from_timestring(ts):

        # 2018-08-14 07:28:05+00:00
        # 2022-06-20 22:50:49.347000+00:00
        t = re.compile("^(\\d\\d\\d\\d)-(\\d\\d)-(\\d\\d)[T| ](\\d\\d):(\\d\\d):(\\d+).*?\\+00:00").findall(ts)
        if t:
            std = f"{t[0][0]}-{t[0][1]}-{t[0][2]} {t[0][3]}:{t[0][4]}:{t[0][5]} +0000"
            return datetime.datetime.strptime(std, "%Y-%m-%d %H:%M:%S %z")

        # 2018-08-04T07:46:37.000Z
        # 2018-08-04T07:44:45Z
        t = re.compile("^(\\d\\d\\d\\d)-(\\d\\d)-(\\d\\d)[T| ](\\d\\d):(\\d\\d):(\\d+).*?Z").findall(ts)
        if t:
            std = f"{t[0][0]}-{t[0][1]}-{t[0][2]} {t[0][3]}:{t[0][4]}:{t[0][5]} +0000"
            return datetime.datetime.strptime(std, "%Y-%m-%d %H:%M:%S %z")

        # 20180804T074445Z
        # 20180804Z074445
        t = re.compile("^(\\d\\d\\d\\d)(\\d\\d)(\\d\\d)[T|Z](\\d\\d)(\\d\\d)(\\d+)[Z]?").findall(ts)
        if t:
            std = f"{t[0][0]}-{t[0][1]}-{t[0][2]} {t[0][3]}:{t[0][4]}:{t[0][5]} +0000"
            return datetime.datetime.strptime(std, "%Y-%m-%d %H:%M:%S %z")

        # 1533378888
        # 1533373930.983988
        t = re.compile("^(\\d+)(\\.\\d+)?").findall(ts)
        if t:
            std = datetime.datetime.fromtimestamp(float(f"{t[0][0]}{t[0][1]}"))
            return pytz.timezone("UTC").localize(std)

        return None

    datetime_obj = datetime_from_timestring(ts=str(timestring))

    if not datetime_obj:
        raise ConfigSyncException("Unknown timestamp format supplied, unable to normalize", timestring)

    if target_timezone:
        datetime_obj = datetime_obj.astimezone(pytz.timezone(target_timezone))

    return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
