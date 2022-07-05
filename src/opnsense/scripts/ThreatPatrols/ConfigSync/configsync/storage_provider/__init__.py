"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
"""

import logging

from configsync.exceptions import ConfigSyncException
from configsync.utils.config_helpers import read_configfile

from configsync.vars import (
    __title__,
    __configsync_config_filename__,
    __configsync_config_settings__,
    __configsync_boto3_providers__,
    __configsync_azure_providers__,
)

logger = logging.getLogger(__title__)


class StorageProvider:

    storage_provider = None

    def __init__(self, **kwargs):

        if kwargs["config_filename"]:
            config_filename = kwargs["config_filename"]
        else:
            config_filename = __configsync_config_filename__

        if config_filename.startswith("TEST_"):
            # do not load any configuration or import any kwargs
            self.__instantiate_storage_provider(provider=kwargs["provider"], params={})
            return

        config = read_configfile(filename=config_filename, section="storage_provider")

        params = {}
        for config_setting in __configsync_config_settings__:
            if config_setting in kwargs and kwargs[config_setting]:
                params[config_setting] = kwargs[config_setting]
            elif isinstance(config, dict) and config_setting in config and config[config_setting]:
                params[config_setting] = config[config_setting]

        if "provider" not in params:
            raise ConfigSyncException("Provider not set in configuration file; is the configsync service enabled?")

        self.__instantiate_storage_provider(provider=params["provider"], params=params)

    def __instantiate_storage_provider(self, provider, params):

        if provider in __configsync_boto3_providers__:
            from configsync.storage_provider.boto3_compatible import StorageProviderBoto3Compatible

            self.storage_provider = StorageProviderBoto3Compatible(**params)

        elif provider in __configsync_azure_providers__:
            from configsync.storage_provider.azure_blob_storage import StorageProviderAzureBlobStorage

            self.storage_provider = StorageProviderAzureBlobStorage(**params)

        else:
            raise ConfigSyncException("Unknown storage provider requested", provider)

    def test_parameters(self, **kwargs):
        return self.storage_provider.test_parameters(**kwargs)

    def sync_current_system_config(self):
        return self.storage_provider.sync_current_system_config()

    def sync_all_system_configs(self):
        return self.storage_provider.sync_all_system_configs()

    def list_synced_system_configs(self, filter_expression=None):
        return self.storage_provider.list_synced_system_configs(filter_expression=filter_expression)
