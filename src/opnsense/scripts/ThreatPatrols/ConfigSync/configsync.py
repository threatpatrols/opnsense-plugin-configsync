#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification,
    are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import json
import logging
import argparse
from signal import signal, SIGINT

from configsync.utils.logger_helpers import init_logger
from configsync.storage_provider import StorageProvider
from configsync.exceptions import ConfigSyncException

from configsync.__version__ import __version__

from configsync.vars import __title__
from configsync.vars import __logging_console_level__
from configsync.vars import __logging_syslog_level__
from configsync.vars import __configsync_config_settings__
from configsync.vars import __configsync_boto3_providers__
from configsync.vars import __configsync_azure_providers__


logger = logging.getLogger(__title__)


def sigint_handler(__signal_received, __frame):
    print("SIGINT received, exiting.")
    sys.exit(1)


def configsync_cli():

    # args
    args = __argparse()

    # extract the required params from args if this is not a test_ action
    if args.action.startswith("test_"):
        params = {"provider": args.provider, "config_filename": "TEST_ACTION_DONT_LOAD_CONFIG"}
    else:
        param_keys = __configsync_config_settings__ + ["config_filename"]
        params = {k: v for k, v in args.__dict__.items() if k in param_keys}

    # action - version
    if args.action == "version":
        return {"version": __version__}

    storage_provider = StorageProvider(**params)

    # action - test_parameters
    if args.action == "test_parameters":
        return storage_provider.test_parameters(
            provider=args.provider,
            bucket=args.bucket,
            endpoint=args.endpoint,
            path=args.path,
            key_id=args.key_id,
            key_secret=args.key_secret,
        )

    # action - sync_current_system_config
    elif args.action == "sync_current_system_config":
        return storage_provider.sync_current_system_config()

    # action - sync_all_system_configs
    elif args.action == "sync_all_system_configs":
        return storage_provider.sync_all_system_configs()

    # action - list_synced_system_configs
    elif args.action == "list_synced_system_configs":
        return storage_provider.list_synced_system_configs(filter_expression=args.filter)

    raise ConfigSyncException("Unknown action requested", args.action)


def __argparse():

    parser = argparse.ArgumentParser(add_help=True, description="Configuration Sync for OPNsense")

    parser.add_argument("--debug", action="store_true", help="Set logging to DEBUG level")

    parser.add_argument(
        "action",
        type=str,
        metavar="<action>",
        choices=[
            "test_parameters",
            "sync_current_system_config",
            "sync_all_system_configs",
            "list_synced_system_configs",
            "version",
        ],
        help="Interface action requested",
    )

    parser.add_argument(
        "--provider",
        type=str,
        metavar="<provider>",
        required=False,
        choices=__configsync_boto3_providers__,
        help='Overrides the storage provider "provider" value from configsync.conf',
    )
    parser.add_argument(
        "--bucket",
        type=str,
        metavar="<bucket>",
        required=False,
        help='Overrides the storage provider "bucket" value from configsync.conf',
    )
    parser.add_argument(
        "--endpoint",
        type=str,
        metavar="<endpoint>",
        required=False,
        help='Overrides the storage provider "endpoint" value from configsync.conf',
    )

    parser.add_argument(
        "--path",
        type=str,
        metavar="<path>",
        required=False,
        help='Overrides the storage provider "path" value from configsync.conf',
    )

    parser.add_argument(
        "--key-id",
        type=str,
        metavar="<key-id-value>",
        required=False,
        help='Overrides the storage provider "key_id" value from configsync.conf',
    )
    parser.add_argument(
        "--key-secret",
        type=str,
        metavar="<key-secret-value>",
        required=False,
        help='Overrides the storage provider "key_secret" value from configsync.conf',
    )

    parser.add_argument(
        "--filter",
        type=str,
        metavar="<filter-expression>",
        required=False,
        help="Filter expression used with the list_synced_system_configs action",
    )

    parser.add_argument(
        "--config-filename",
        type=str,
        metavar="<config-filename>",
        required=False,
        help="ConfigSync configuration file config override, not to be confused with the system (.xml file) config",
    )

    parsed_args = parser.parse_args()

    for arg_name in vars(parsed_args):
        value = getattr(parsed_args, arg_name)
        if len(str(value)) == 0:
            setattr(parsed_args, arg_name, None)

    return parsed_args


if __name__ == "__main__":
    signal(SIGINT, sigint_handler)

    if "--debug" in sys.argv:
        debug = True
        init_logger(console_level="debug", syslog_level="debug")
    else:
        debug = False
        init_logger(console_level=__logging_console_level__, syslog_level=__logging_syslog_level__)

    try:
        response = configsync_cli()

    except ConfigSyncException as e:
        message = str(e).strip()
        logger.error(message)
        response = {
            "status": "fail",
            "message": message,
        }

    except Exception as e:  # noqa pylint:disable=broad-except
        message = str(e).strip()
        logger.critical(msg=message, exc_info=debug)  # provides stacktrace if debug mode
        response = {
            "status": "fail",
            "message": message,
        }

    print(json.dumps(response, default=str, sort_keys=True, indent="  "))
