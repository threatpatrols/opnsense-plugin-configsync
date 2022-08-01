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
import os
import logging
import boto3

from configsync.exceptions import ConfigSyncException

from configsync.utils.file_helpers import read_consistent
from configsync.utils.content_helpers import gzip_content
from configsync.utils.content_helpers import normalize_timestamp
from configsync.utils.file_helpers import file_metadata
from configsync.utils.digest_helpers import content_digest
from configsync.utils.system_helpers import get_system_hostname
from configsync.utils.system_helpers import get_system_hostid

from configsync.vars import __title__
from configsync.vars import __configsync_config_settings__
from configsync.vars import __configsync_gzip_content__
from configsync.vars import __configsync_digest_method__
from configsync.vars import __storage_provider_default_acl__
from configsync.vars import __storage_provider_max_keys_per_request__
from configsync.vars import __system_config_current_file__
from configsync.vars import __system_config_backups_path__


logger = logging.getLogger(__title__)


class StorageProviderBoto3Compatible:

    provider = None
    bucket = None
    endpoint = None
    path = None
    key_id = None
    key_secret = None

    def __init__(self, **kwargs):

        for config_setting in __configsync_config_settings__:
            if config_setting in kwargs and kwargs[config_setting]:
                setattr(self, config_setting, kwargs[config_setting])

        self.endpoint = self.__endpoint_url(provider=self.provider, bucket=self.bucket, url=self.endpoint)

    def test_parameters(self, **kwargs):
        """
        Sets up StorageProviderBoto3Compatible() using the function-args parameters and then attempts to
        upload the current config to filename "config-test.xml" - provides response status and data

        :param kwargs:
        :return:
        """
        logger.debug(f"test_parameters({kwargs})")

        # Setup this test instance of StorageProviderBoto3Compatible()
        for config_setting in __configsync_config_settings__:
            setattr(self, config_setting, kwargs[config_setting])

        self.endpoint = self.__endpoint_url(provider=self.provider, bucket=self.bucket, url=self.endpoint)

        # config-test.xml
        config_files = [
            {
                "source_filepath": __system_config_current_file__,
                "target_filename": "config-test.xml",
                "content_type": "application/xml",
            }
        ]

        # perform this test sync action
        return self.__sync_files(files=config_files, overwrite_existing=True)

    def sync_current_system_config(self):
        """
        Sync's the current system config file to the storage provider, overwriting any existing config-current.xml
        file on storage provider

        :return:
        """
        logger.debug("sync_current_system_config()")

        config_files = [
            {
                "source_filepath": __system_config_current_file__,
                "target_filename": "config-current.xml",
                "content_type": "application/xml",
            }
        ]

        response = self.__sync_files(files=config_files, overwrite_existing=True)
        self.__response_to_logger(action="sync_current_system_config", response=response)
        return response

    def sync_all_system_configs(self):
        """
        Creates a list of all the system configuration files and syncs them to the storage provider, will not
        overwrite any existing file on the storage provider.

        :return:
        """
        logger.debug("sync_all_system_configs()")

        config_files = [
            {
                "source_filepath": __system_config_current_file__,
                "target_filename": "config-current.xml",
                "content_type": "application/xml",
            }
        ]

        for backup_filename in os.listdir(__system_config_backups_path__):
            if backup_filename.startswith("config") and backup_filename.endswith(".xml"):
                config_files.append(
                    {
                        "source_filepath": os.path.join(__system_config_backups_path__, backup_filename),
                        "target_filename": backup_filename,
                        "content_type": "application/xml",
                    }
                )

        response = self.__sync_files(files=config_files, overwrite_existing=False)
        self.__response_to_logger(action="sync_all_system_configs", response=response)
        return response

    def list_synced_system_configs(self, filter_expression=None):
        """
        Provides a list of the currently stored configuration files on the configured storage_provider

        :param filter_expression:
        :return:
        """
        logger.debug(f"list_synced_system_configs(filter_expression={filter_expression})")

        response = self.__list_objects()
        if response["status"] != "success":
            return response

        sorted_items = []
        for filename_key in sorted(response["data"].keys(), reverse=True):
            if filter_expression is None or len(filter_expression) == 0:
                sorted_items.append(response["data"][filename_key])
            else:
                if filter_expression in filename_key:
                    sorted_items.append(response["data"][filename_key])

        response["message"] += f" where {len(sorted_items)} file objects match filter:{filter_expression}"
        response["data"] = sorted_items
        return response

    def __sync_files(self, files, overwrite_existing=False) -> dict:
        """
        Uses functions __list_objects and __put_object() to incrementally sync a list of files to the storage_provider

        :param files:
        :param overwrite_existing:
        :return:
        """
        logger.debug(f"__sync_files(<files>, overwrite_existing={overwrite_existing})")

        existing_files = {}

        if overwrite_existing is False:
            response = self.__list_objects()
            if response["status"] != "success":
                return response
            if "data" in response:
                existing_files = response["data"]

        put_files = []
        for put_file_candidate in files:
            if put_file_candidate["target_filename"] not in existing_files.keys():
                put_files.append(put_file_candidate)

        if len(put_files) == 0:
            return {
                "status": "success",
                "message": f"No files required for PUT into bucket:{self.bucket} in path:{self.path}",
            }

        for put_file in put_files:

            content = read_consistent(filename=put_file["source_filepath"])
            content_encoding = None
            if __configsync_gzip_content__:
                content = gzip_content(content=content)
                content_encoding = "gzip"

            filemetadata = file_metadata(filename=put_file["source_filepath"], digest_value=True)
            object_tags = {
                "filetype": "opnsense-config",
                "mtime": str(filemetadata["mtime"]),
                "bytes": str(filemetadata["bytes"]),
                __configsync_digest_method__: str(filemetadata["digest"]),
                "hostid": get_system_hostid(),
                "hostname": get_system_hostname(),
            }

            response = self.__put_object(
                filename=put_file["target_filename"],
                content=content,
                content_type=put_file["content_type"],
                content_encoding=content_encoding,
                object_tags=object_tags,
            )
            if response["status"] != "success":
                return response

        return {
            "status": "success",
            "message": f"Successful PUT {len(put_files)} objects into bucket:{self.bucket} in path:{self.path}",
            "data": put_files,
        }

    def __put_object(self, filename, content, content_type=None, content_encoding=None, object_tags=None) -> dict:
        """
        Uses Boto3 to PUT a file into the storage_provider

        :param target_filename:
        :param content:
        :param content_type:
        :param content_encoding:
        :param object_tags:
        :return:
        """
        logger.debug(
            f"__put_object(filename={filename}, <content>, content_type={content_type}, "
            f"content_encoding={content_encoding}, <object_tags>)"
        )

        client_params = {
            # ACL causes Google Cloud Storage to break when uniform bucket-level access enabled
            # "ACL": __storage_provider_default_acl__,
            "Body": content,
            "Bucket": self.bucket,
            "Key": f"{self.path}/{filename}".strip("/"),
            "ContentLength": len(content),
            f"Content{__configsync_digest_method__.upper()}": content_digest(content, digest_type="base64"),
        }

        if self.path is None:
            raise ConfigSyncException("Unexpected value storage_provider:path is None")

        logger.debug(f"__put_object() - provider={self.provider}")
        logger.debug(f"__put_object() - endpoint={self.endpoint}")
        logger.debug(f"__put_object() - client_params[Key]={client_params['Key']}")

        if content_type:
            client_params["ContentType"] = content_type

        if content_encoding:
            client_params["ContentEncoding"] = content_encoding

        if object_tags:
            client_params["Metadata"] = object_tags

        boto_client = boto3.client(
            "s3", aws_access_key_id=self.key_id, aws_secret_access_key=self.key_secret, endpoint_url=self.endpoint
        )

        response = boto_client.put_object(**client_params)

        status_code = None
        try:
            status_code = int(response["ResponseMetadata"]["HTTPStatusCode"])
        except Exception:
            pass

        if status_code and status_code == 200:
            return {
                "status": "success",
                "message": f"Successful PUT object in bucket:{self.bucket} with key:{client_params['Key']}",
                "data": client_params["Key"],
            }

        return {
            "status": "fail",
            "message": f"Unable to PUT object in bucket:{self.bucket} with "
            f"key:{client_params['Key']} (HTTPStatusCode: {status_code})",
            "data": client_params["Key"],
        }

    def __list_objects(self, continuation_token=None, max_keys_per_request=None) -> dict:
        """
        Uses Boto3 to get a list of the objects at the storage_provider

        :param continuation_token:
        :param max_keys_per_request:
        :return:
        """
        logger.debug(
            f"__list_objects(continuation_token={continuation_token}, max_keys_per_request={max_keys_per_request})"
        )

        if not max_keys_per_request:
            max_keys_per_request = __storage_provider_max_keys_per_request__

        client_params = {
            "Bucket": self.bucket,
            "MaxKeys": max_keys_per_request,
            "Prefix": self.path,
        }
        if continuation_token:
            client_params["ContinuationToken"] = continuation_token

        client = boto3.client(
            "s3", aws_access_key_id=self.key_id, aws_secret_access_key=self.key_secret, endpoint_url=self.endpoint
        )

        response = client.list_objects_v2(**client_params)

        file_objects = {}
        if "Contents" in response:
            for object_item in response["Contents"]:
                if object_item["Key"].endswith("/") and object_item["Size"] == 0:
                    continue  # skip because not a file
                filename = os.path.basename(object_item["Key"])
                file_objects[filename] = object_item
                file_objects[filename]["LastModified"] = normalize_timestamp(object_item["LastModified"])
                file_objects[filename]["ETag"] = object_item["ETag"].strip('"')

        if continuation_token is None and len(file_objects) == 0:
            return {
                "status": "success",
                "message": f"No file objects found in bucket:{self.bucket} in path:{self.path}",
            }

        if "NextContinuationToken" in response:
            next_data = self.__list_objects(
                continuation_token=response["NextContinuationToken"], max_keys_per_request=max_keys_per_request
            )
            if next_data["status"] != "success":
                return next_data
            file_objects = {**file_objects, **next_data["data"]}

        return {
            "status": "success",
            "message": f"Success listing {len(file_objects)} file objects in "
            f"bucket:{self.bucket} in path:{self.path}",
            "data": file_objects,
        }

    def __endpoint_url(self, provider=None, bucket=None, url=None):
        """
        Generate an endpoint url for the respective boto3 compatible storage_provider

        :param provider:
        :param bucket:
        :param url:
        :return:
        """

        if url:
            return url

        if not provider and not bucket and not url:  # occurs when using the test_parameters action
            return None

        if not provider or not bucket:
            raise ConfigSyncException("Both provider and bucket values must be set if endpoint:url is not set")

        if provider.startswith("aws"):
            return f"https://{bucket}.s3.amazonaws.com"

        elif provider.startswith("google"):
            return "https://storage.googleapis.com"

        elif provider.startswith("digitalocean"):
            raise ConfigSyncException("DigitalOcean must be setup using endpoint:url")

        elif provider.startswith("other"):
            raise ConfigSyncException("Other S3 compatible storage providers must be setup using endpoint:url")

        raise ConfigSyncException("Unknown provider requested", provider)

    def __response_to_logger(self, action, response):
        if "message" in response and "status" in response:
            if response["status"].lower() == "success":
                logger.info(f"{action} - {response['message']}")
            else:
                logger.warning(f"{action} - {response['message']}")
