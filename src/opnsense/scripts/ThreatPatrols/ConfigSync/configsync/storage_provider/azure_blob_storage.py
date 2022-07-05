"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
"""

from configsync.exceptions import ConfigSyncException


class StorageProviderAzureBlobStorage:

    endpoint = None
    bucket = None
    path = None
    key_id = None
    key_secret = None

    def __init__(self, **kwargs):
        raise ConfigSyncException("Azure Blob Storage not (yet) implemented")
