#!/usr/local/bin/python2.7

import os
import json
import gzip
import time
import random
import shutil
import hashlib
import StringIO
import subprocess
import ConfigParser

from xmltodict import xmltodict


class StorageInterfaceException(Exception):
    pass


class StorageInterface(object):

    system_config_backups_path='/conf/backup'
    system_config_current_file='/conf/config.xml'
    service_config_file='/usr/local/etc/configsync/configsync.conf'

    def read_consistent(self, filename, return_meta=None, __attempt=1, __max_attempts=16):

        if __attempt >= __max_attempts:
            raise StorageInterfaceException('Too many retries while attempting to call read_consistent_local_file()')

        if return_meta is None:
            return_meta = []

        digest_method = 'sha256'
        if 'md5' in return_meta:
            digest_method = 'md5'
        if 'sha1' in return_meta:
            digest_method = 'sha1'

        random_chars = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(8))
        tempfile_0 = '/tmp/read_consistent.{}.0'.format(random_chars)
        tempfile_1 = '/tmp/read_consistent.{}.1'.format(random_chars)

        subprocess.call(['/bin/sync'])
        shutil.copy(filename, tempfile_0)
        digest_0 = self.file_digest(tempfile_0, digest_method=digest_method, output_type='hexdigest')
        mtime_0 = os.path.getmtime(filename)
        bytes_0 = os.path.getsize(filename)

        time.sleep(0.054193)

        subprocess.call(['/bin/sync'])
        shutil.copy(filename, tempfile_1)
        digest_1 = self.file_digest(tempfile_1, digest_method=digest_method, output_type='hexdigest')

        if digest_0 != digest_1:
            os.unlink(tempfile_0)
            os.unlink(tempfile_1)
            time.sleep(0.104729)
            return self.read_consistent(filename, __attempt=__attempt + 1)

        with open(tempfile_0, 'rb') as f:
            content = f.read()

        os.unlink(tempfile_0)
        os.unlink(tempfile_1)
        if return_meta is not None:
            meta = {}
            if 'md5' in return_meta:
                meta['md5'] = digest_0
            if 'sha1' in return_meta:
                meta['sha1'] = digest_0
            if 'sha256' in return_meta:
                meta['sha256'] = digest_0
            if 'mtime' in return_meta:
                meta['mtime'] = mtime_0
            if 'bytes' in return_meta:
                meta['bytes'] = bytes_0
            return content, meta
        return content

    def file_digest(self, filename, digest_method='md5', output_type='hexdigest', buffer_size=4096):

        if digest_method == 'md5':
            digest = hashlib.md5()
        elif digest_method == 'sha1':
            digest = hashlib.sha1()
        elif digest_method == 'sha256':
            digest = hashlib.sha256()
        else:
            raise StorageInterfaceException('Unsupported digest method', digest_method)

        with open(filename, 'rb') as f:
            while True:
                data = f.read(buffer_size)
                if not data:
                    break
                digest.update(data)

        if output_type == 'base64':
            return digest.digest().encode('base64').strip()
        elif output_type == 'hexdigest':
            return digest.hexdigest()
        raise StorageInterfaceException('Unsupported output type', output_type)

    def content_digest(self, content, digest_method='md5', output_type='hexdigest', buffer_size=4096):

        if digest_method == 'md5':
            digest = hashlib.md5()
        elif digest_method == 'sha1':
            digest = hashlib.sha1()
        elif digest_method == 'sha256':
            digest = hashlib.sha256()
        else:
            raise StorageInterfaceException('Unsupported digest method', digest_method)

        digest.update(content)

        if output_type == 'base64':
            return digest.digest().encode('base64').strip()
        elif output_type == 'hexdigest':
            return digest.hexdigest()
        raise StorageInterfaceException('Unsupported output type', output_type)

    def get_system_hostid(self):
        hostid = '00000000-0000-0000-0000-000000000000'
        if os.path.isfile('/etc/hostid'):
            with open('/etc/hostid', 'r') as f:
                hostid = f.read().strip()
        return hostid

    def get_system_hostname(self):
        return subprocess.check_output(['/bin/hostname', '-s']).strip().lower()

    def gzip_content(self, content):
        out = StringIO.StringIO()
        with gzip.GzipFile(fileobj=out, mode='wb') as f:
            f.write(content)
        return out.getvalue()

    def xml_to_dict(self, xml):
        return xmltodict.parse(xml_input=xml)

    def read_config(self, section):
        if not os.path.isfile(self.service_config_file):
            return None

        config = ConfigParser.ConfigParser()
        config.read(self.service_config_file)

        if section not in config.sections():
            return None

        configuration = {}
        for option, value in config.items(section):
            configuration[str(option).lower()] = str(value)

        return configuration

    def response_output(self, message, status='success', data=None):

        if status.lower() == 'okay' or status.lower() == 'ok':
            status = 'success'

        response_data = {
            'status': status.lower(),
            'message': message,
            'timestamp': time.time()
        }

        if data is not None:
            response_data['data'] = data

        print (json.dumps(response_data))
        return response_data
