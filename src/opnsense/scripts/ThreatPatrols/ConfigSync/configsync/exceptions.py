"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
"""


class ConfigSyncException(Exception):
    def __init__(self, *args):
        args_decoded = []
        for _, arg_value in enumerate(args):
            if isinstance(arg_value, bytes):
                args_decoded.append(arg_value.decode("utf8"))
            else:
                args_decoded.append(arg_value)
        super().__init__(*args_decoded)
