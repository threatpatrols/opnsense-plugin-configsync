<?php

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
        'pidfile' => '/var/run/configsync-monitord.pid'
    );

    return $services;
}
