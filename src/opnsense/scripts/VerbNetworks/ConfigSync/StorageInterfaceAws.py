#!/usr/local/bin/python2.7

import os
import urllib
import argparse
import requests

from requestsaws.awsauth import S3Auth
from StorageInterface import StorageInterface


class StorageInterfaceAwsException(Exception):
    pass


class StorageInterfaceAws(StorageInterface):

    storage_configs_full_path='{storage_path}/{hostname}'
    storage_use_gzip_encoding=True
    aws_request_timeout = 30

    __aws_key_id = None
    __aws_key_secret = None

    def main(self):

        parser = argparse.ArgumentParser(description='AWS S3 storage interface for ConfigSync')
        parser.add_argument('action', type=str, choices=['test_parameters', 'sync_config_current', 'sync_config_missing'], help='Interface action requested')
        parser.add_argument('--key_id', type=str, help='AWS key id')
        parser.add_argument('--key_secret', type=str, help='AWS key secret')
        parser.add_argument('--bucket', type=str, help='AWS S3 bucket name')
        parser.add_argument('--path', type=str, help='Base path within the bucket to use')

        args = parser.parse_args()

        if not os.path.isfile(self.system_config_current_file):
            return {'status': 'fail', 'message': 'Unable to locate configuration file', 'data': self.system_config_current_file}

        if not os.path.isdir(self.system_config_backups_path):
            return {'status': 'fail', 'message': 'Unable to locate configuration backups path', 'data': self.system_config_backups_path}

        if args.action == 'test_parameters':
            return self.test_parameters(key_id=args.key_id, key_secret=args.key_secret, bucket=args.bucket, path=args.path)
        elif args.action == 'sync_config_current':
            return self.sync_config_current()
        elif args.action == 'sync_config_missing':
            return self.sync_config_missing()

        return {'status': 'fail', 'message': 'Unable to invoke StorageInterfaceAws of ConfigSync'}

    def test_parameters(self, key_id, key_secret, bucket, path):

        # check that the parameters seem valid
        if key_id is None or len(key_id) == 0:
            return {'status': 'fail', 'message': 'Parameter key_id cannot be empty'}
        if key_secret is None or len(key_secret) == 0:
            return {'status': 'fail', 'message': 'Parameter key_secret cannot be empty'}
        if bucket is None or len(bucket) == 0:
            return {'status': 'fail', 'message': 'Parameter bucket cannot be empty'}
        if path is None or len(path) == 0:
            return {'status': 'fail', 'message': 'Parameter path cannot be empty'}

        # assign the aws credentials provided
        self.__aws_key_id = key_id
        self.__aws_key_secret = key_secret

        try:
            content, meta = self.read_consistent(self.system_config_current_file, return_meta=['mtime', 'md5', 'bytes'])
        except(Exception) as e:
            return {
                'status': 'fail',
                'message': 'Unable to obtain consistent read of {}'.format(self.system_config_current_file),
                'data': str(e)
            }

        target_path = self.storage_configs_full_path.format(
                            storage_path=path,
                            hostname=self.get_system_hostname()
        ) + '/' + 'config-current.xml'

        response = self.put_object(
            bucket=bucket,
            path=target_path,
            content=content if self.storage_use_gzip_encoding is not True else self.gzip_content(content),
            content_encoding=None if self.storage_use_gzip_encoding is not True else 'gzip',
            content_type='application/xml',
            object_tags={
                'filetype': 'opnsense-config',
                'mtime': str(meta['mtime']),
                'bytes': str(meta['bytes']),
                'md5': str(meta['md5']),
                'hostid': self.get_system_hostid(),
            }
        )

        return response

    def sync_config_current(self):
        config_list = [(self.system_config_current_file, 'config-current.xml')]
        return self.sync_configs(config_list, overwrite_existing=True)

    def sync_config_missing(self):
        config_list = [(self.system_config_current_file, 'config-current.xml')]
        for backup_file in os.listdir(self.system_config_backups_path):
            if backup_file.endswith('.xml'):
                config_list.append((os.path.join(self.system_config_backups_path, backup_file), backup_file))
        return self.sync_configs(config_list, overwrite_existing=False)

    def sync_configs(self, config_list, overwrite_existing=False):
        config = self.read_config('awss3')

        if config is None:
            return {'status': 'fail', 'message': 'No configuration for awss3 available' }

        if int(config['enabled']) != 1:
            return {'status': 'fail', 'message': 'Service is not enabled' }

        self.__aws_key_id = config['providerkey']
        self.__aws_key_secret = config['providersecret']

        existing_configs = {}
        if overwrite_existing is False:
            prefix_path = self.storage_configs_full_path.format(
                storage_path=config['storagepath'],
                hostname=self.get_system_hostname()
            )
            list_response = self.list_objects(config['storagebucket'], prefix_path)
            if list_response['status'] != 'success':
                return list_response
            existing_configs = list_response['data']

        target_paths = []
        for config_item in config_list:
            source_path, target_filename = config_item

            if overwrite_existing is False:
                if target_filename in existing_configs.keys():
                    continue

            try:
                content, meta = self.read_consistent(source_path, return_meta=['mtime', 'md5', 'bytes'])
            except(Exception) as e:
                return {
                    'status': 'fail',
                    'message': 'Unable to obtain consistent read of {}'.format(source_path),
                    'data': str(e)
                }

            target_path = self.storage_configs_full_path.format(
                            storage_path=config['storagepath'],
                            hostname=self.get_system_hostname()
            ) + '/' + target_filename

            target_paths.append(target_path)

            put_response = self.put_object(
                bucket=config['storagebucket'],
                path=target_path,
                content=content if self.storage_use_gzip_encoding is not True else self.gzip_content(content),
                content_encoding=None if self.storage_use_gzip_encoding is not True else 'gzip',
                content_type='application/xml',
                object_tags={
                    'filetype': 'opnsense-config',
                    'mtime': str(meta['mtime']),
                    'bytes': str(meta['bytes']),
                    'md5': str(meta['md5']),
                    'hostid': self.get_system_hostid(),
                }
            )

            if put_response['status'] != 'success':
                return put_response

        return {'status': 'success', 'message': 'Successfully PUT all AWS S3 objects', 'data': target_paths}

    def put_object(self, bucket, path, content, content_type=None, content_encoding=None, object_tags=None):

        url = 'https://{}.s3.amazonaws.com/{}'.format(bucket, path)

        headers = {}
        headers['Content-MD5'] = self.content_digest(content, digest_method='md5', output_type='base64')

        if content_type is not None:
            headers['Content-Type'] = content_type

        if content_encoding is not None:
            headers['Content-Encoding'] = content_encoding

        if object_tags is not None and type(object_tags) is dict:
            for tag_key, tag_value in object_tags.items():
                headers['x-amz-meta-{}'.format(tag_key)] = tag_value

        try:
            r = requests.put(url, data=content, headers=headers, auth=S3Auth(self.__aws_key_id, self.__aws_key_secret), timeout=self.aws_request_timeout)
        except(Exception) as e:
            return {
                'status': 'fail',
                'message': 'Exception',
                'data': str(e)
            }

        if r.status_code not in (200, 204):
            if 'Content-Type' in r.headers and r.headers['Content-Type'] == 'application/xml':
                error_data = self.xml_to_dict(r.content)
                if 'Error' in error_data and 'Message' in error_data['Error']:
                    error = error_data['Error']['Message']
                else:
                    error = error_data
            else:
                error = r.content
            return {
                'status': 'fail',
                'message': 'Unable to PUT object',
                'data': error
            }
        return {
            'status': 'success',
            'message': 'Successful AWS S3 object PUT',
            'data': url
        }

    def list_objects(self, bucket, path, continuation_token=None, max_keys=1000):

        params = {'list-type': 2, 'max-keys': max_keys, 'prefix': path}
        if continuation_token is not None:
            params['continuation-token'] = continuation_token

        url = 'https://{}.s3.amazonaws.com/?{}'.format(bucket, urllib.urlencode(params))

        try:
            r = requests.get(url, auth=S3Auth(self.__aws_key_id, self.__aws_key_secret), timeout=self.aws_request_timeout)
        except(Exception) as e:
            return {
                'status': 'fail',
                'message': 'Exception',
                'data': str(e)
            }

        if r.status_code not in (200, 204):
            if 'Content-Type' in r.headers and r.headers['Content-Type'] == 'application/xml':
                error_data = self.xml_to_dict(r.content)
                if 'Error' in error_data and 'Message' in error_data['Error']:
                    error = error_data['Error']['Message']
                else:
                    error = error_data
            else:
                error = r.content
            return {
                'status': 'fail',
                'message': 'Unable to GET object list',
                'data': error
            }

        if 'Content-Type' in r.headers and r.headers['Content-Type'] == 'application/xml':
            data = self.xml_to_dict(r.content)

            contents = {}
            if 'ListBucketResult' in data and 'Contents' in data['ListBucketResult']:
                if 'Key' in data['ListBucketResult']['Contents']:
                    data['ListBucketResult']['Contents'] = [data['ListBucketResult']['Contents']]
                for item in data['ListBucketResult']['Contents']:
                    item['ETag'] = item['ETag'].strip('"')
                    contents[os.path.basename(item['Key'])] = item

            if 'ListBucketResult' in data and 'NextContinuationToken' in data['ListBucketResult']:
                next_token = data['ListBucketResult']['NextContinuationToken']
                next_data = self.list_objects(bucket, path, continuation_token=next_token, max_keys=max_keys)
                if next_data['status'] != 'success':
                    return {'status': 'fail', 'message': next_data['message'], 'data': next_data['data']}
                contents.update(next_data['data'])

            return {
                'status': 'success',
                'message': 'Successful AWS S3 object list GET',
                'data': contents
            }
        return {
            'status': 'fail',
            'message': 'Response data is not XML format as expected',
            'data': r.content
        }


if __name__ == '__main__':
    Interface = StorageInterfaceAws()
    Interface.response_output(**Interface.main())
