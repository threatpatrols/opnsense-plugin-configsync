"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
"""

__title__ = "configsync"

__logging_syslog_level__ = "info"
__logging_console_level__ = "info"

__configsync_gzip_content__ = True
__configsync_digest_method__ = "md5"  # NB: cryptographic strength not essential for content equality tests here
__configsync_read_consistent_min_max__ = (0.1, 0.2)  # (MIN, MAX) in seconds
__configsync_config_filename__ = "/usr/local/etc/configsync/configsync.conf"
__configsync_config_settings__ = ["provider", "bucket", "endpoint", "path", "key_id", "key_secret"]
__configsync_boto3_providers__ = ["aws_s3", "google_cloud_storage", "digitalocean_spaces", "other_s3_compatible"]
__configsync_azure_providers__ = ["azure_blob_storage"]  # NB: Azure storage provider not implemented

__storage_provider_default_acl__ = "private"
__storage_provider_max_keys_per_request__ = 999

__system_sync_bin__ = "/bin/sync"
__system_hostid_file__ = "/etc/hostid"

__system_config_backups_path__ = "/conf/backup"
__system_config_current_file__ = "/conf/config.xml"
