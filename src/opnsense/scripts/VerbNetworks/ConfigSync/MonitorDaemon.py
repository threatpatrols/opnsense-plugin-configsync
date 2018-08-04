#!/usr/local/bin/python2.7

import os
import sys
import time
import json
import syslog
import argparse
import subprocess
import ConfigParser

sys.path.insert(0, "/usr/local/opnsense/site-python")
from daemonize import Daemonize


MONITORDAEMON_PIDFILE='/var/run/configsync-monitordaemon.pid'


class MonitorDaemonException(Exception):
    pass


class MonitorDaemon(object):

    name = 'configsync-monitordaemon'

    config_file = None
    config_file_mtime = None
    foreground = None
    debug = None
    enabled = None
    monitors = None
    interval = None

    def __init__(self):
        syslog.openlog(self.name, logoption=syslog.LOG_DAEMON, facility=syslog.LOG_LOCAL4)

    def main(self):

        parser = argparse.ArgumentParser(description='configsync-monitordaemon')
        parser.add_argument('--config', '-c', type=str, metavar='<config-file>', required=True,
                            help='Configuration file to use and load')
        parser.add_argument('--foreground', '-F', action='store_true',
                            help='Prevent running as a daemon, keeps process in foreground')
        parser.add_argument('--pid', '-p', type=str, metavar='<pidfile>', default=MONITORDAEMON_PIDFILE,
                            help='PID file location other than {} default'.format(MONITORDAEMON_PIDFILE))
        parser.add_argument('--debug', '-d', action='store_true',
                            help='Enable debug logging output')
        args = parser.parse_args()

        self.config_file = args.config
        self.foreground = args.foreground
        self.debug = args.debug

        if args.foreground is True:
            self.start()
        else:
            daemon = Daemonize(app=self.name, pid=args.pid, action=self.start)
            daemon.start()

    def start(self):
        self.log('info', '{} starting'.format(self.name))

        while os.path.isfile('/var/run/booting') is True:
            self.log('warn', 'Waiting for system to finish boot processing')
            time.sleep(5)

        self.load_configsync_config()

        if self.enabled is not True:
            self.log('info', 'Service is not enabled, exiting')
            return None

        monitor_checksums = []

        self.log('debug', 'Determining initial checksums for each pattern before entering the monitor loop')
        for index, monitor in enumerate(self.monitors):
            checksum = self.get_pattern_checksum(monitor['pattern'])
            self.log('debug', 'Initial checksum for pattern {} is {}'.format(monitor['pattern'], checksum))
            if index not in monitor_checksums:
                monitor_checksums.append(checksum)
            else:
                monitor_checksums[index] = checksum

        self.log('debug', 'Entering monitor loop for detecting change based on recursive md5sum patterns')
        while True:

            try:
                if self.config_file_mtime != os.path.getmtime(self.config_file):
                    self.load_configsync_config()

                if self.enabled is not True:
                    self.log('info', 'Service has been disabled')
                    break

                for index, monitor in enumerate(self.monitors):

                    checksum = self.get_pattern_checksum(monitor['pattern'])
                    if checksum != monitor_checksums[index]:
                        self.log('info', 'Change detected on monitoring pattern {}'.format(monitor['pattern']))

                        try:
                            response = self.command_shell(self.monitors[index]['action'])
                            response_unpacked = json.loads(response)
                            self.log('info', 'Action success on change for pattern {}'.format(monitor['pattern']), data=response_unpacked)
                        except ValueError:
                            self.log('error', 'Action failed on change for pattern {}'.format(monitor['pattern']), data=response)
                        except MonitorDaemonException as e:
                            self.log('error', 'Action failed on change for pattern {}'.format(monitor['pattern']), data=str(e))

                    monitor_checksums[index] = checksum

                self.log('debug', 'Sleeping {} seconds'.format(self.interval))
                time.sleep(self.interval)

            except KeyboardInterrupt:
                break
            except SystemExit:
                break
            except Exception as e:
                self.log('error', 'Unhandled Exception', data=str(e))
                break

        self.log('info', '{} stopping'.format(self.name))
        return None

    def get_pattern_checksum(self, pattern):
        self.log('debug', 'get_pattern_checksum', data=pattern)
        if os.uname()[0].lower() in ['freebsd']:
            md5bin = 'md5'
        else:
            md5bin='md5sum'
        return self.command_shell('{} {} | sort | {} | cut -d" " -f1'.format(md5bin, pattern, md5bin))

    def command_shell(self, command):
        self.log('debug', 'command_shell', data=command)

        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if stderr is not None and len(stderr) > 0:
            raise MonitorDaemonException(stderr.strip())

        return stdout.strip()

    def load_configsync_config(self):
        self.log('info', 'load_configsync_config', data=self.config_file)

        if not os.path.isfile(self.config_file):
            raise MonitorDaemonException('Unable to find configuration file', self.config_file)

        config = ConfigParser.ConfigParser()
        config.read(self.config_file)

        if 'monitordaemon' not in config.sections():
            raise MonitorDaemonException('Unable to locate required configuration section', 'monitordaemon')

        self.config_file_mtime = os.path.getmtime(self.config_file)
        self.log('debug', 'configuration file modify time', data=self.config_file_mtime)

        monitor_configurations = {}
        for option, value in config.items('monitordaemon'):
            if option.lower() == 'enabled':
                self.enabled = True if int(value) == 1 else False
                self.log('debug', 'configuration enabled', data=self.enabled)
            elif option.lower() == 'interval':
                self.interval = int(value)
                self.log('debug', 'configuration interval', data=self.interval)
            else:
                monitor_configurations[option.lower()] = value

        self.monitors = []
        for index in range(0, (len(monitor_configurations)/2 + 1)):
            pattern_key = 'checksumpattern_{}'.format(index)
            action_key = 'action_{}'.format(index)
            if pattern_key not in monitor_configurations.keys() or action_key not in monitor_configurations.keys():
                continue
            self.monitors.append(
                {'pattern': monitor_configurations[pattern_key], 'action': monitor_configurations[action_key]}
            )
        self.log('debug', 'configuration monitors', data=self.monitors)

    def log(self, level, message, data=None):
        level = level.lower()

        if level not in ['debug', 'info', 'warn', 'error', 'fatal']:
            level = 'info'

        log_event = {
            'level': level,
            'message': message,
            'timestamp': time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        }
        syslog_message = message

        if data is not None:
            log_event['data'] = data
            if type(data) is dict and 'data' in data:
                syslog_message += ' {}'.format(json.dumps(data['data']))
            else:
                syslog_message += ' {}'.format(json.dumps(data))

        if level == 'debug':
            # this is a bit crap  :(
            if self.debug is True:
                if self.foreground is True:
                    sys.stderr.write(json.dumps(log_event) + '\n')
                    sys.stderr.flush()
                else:
                    syslog.syslog(syslog.LOG_ALERT, syslog_message)
        else:
            if self.foreground is True:
                sys.stderr.write(json.dumps(log_event) + '\n')
                sys.stderr.flush()
            else:
                syslog.syslog(syslog.LOG_ALERT, syslog_message)

        return log_event


if __name__ == '__main__':
    MonitorDaemon().main()
