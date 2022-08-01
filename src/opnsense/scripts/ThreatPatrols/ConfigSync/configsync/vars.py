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
