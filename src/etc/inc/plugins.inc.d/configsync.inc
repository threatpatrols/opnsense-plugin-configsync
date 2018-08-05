<?php

# Copyright (c) 2018 Verb Networks Pty Ltd <contact [at] verbnetworks.com>
#  - All rights reserved.
#
# Apache License v2.0
#  - http://www.apache.org/licenses/LICENSE-2.0

function configsync_enabled()
{
    $model_configsync = new \VerbNetworks\ConfigSync\ConfigSync();
    return $model_configsync->settings->Enabled->__toString() == "1";
}

function configsync_services()
{
    $services = array();

    if (!configsync_enabled()) {
        return $services;
    }

    $services[] = array(
        'description' => gettext('Configuration Sync Daemon'),
        'configd' => array(
            'restart' => array('configsync restart'),
            'start' => array('configsync start'),
            'stop' => array('configsync stop'),
        ),
        'name' => 'configsync',
        'pidfile' => '/var/run/configsync-monitordaemon.pid'
    );

    return $services;
}

function configsync_syslog()
{
    $logfacilities = array();

    $logfacilities['configsync'] = array(
        'facility' => array('configsync', 'configsync-monitordaemon'),
    );

    return $logfacilities;
}
