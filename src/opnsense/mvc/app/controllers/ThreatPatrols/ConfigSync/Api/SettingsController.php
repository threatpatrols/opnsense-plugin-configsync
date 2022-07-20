<?php

/*
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    Copyright (c) 2018 Verb Networks Pty Ltd <contact@verbnetworks.com>
    Copyright (c) 2018 Nicholas de Jong <me@nicholasdejong.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
*/

namespace ThreatPatrols\ConfigSync\Api;

use OPNsense\Core\Backend;
use OPNsense\Core\Config;
use OPNsense\Base\ApiControllerBase;
use ThreatPatrols\ConfigSync\ConfigSync;

class SettingsController extends ApiControllerBase
{
    public function getAction()
    {
        $response = array();
        if ($this->request->isGet()) {
            $model_ConfigSync = new ConfigSync();
            $response['ConfigSync'] = $model_ConfigSync->getNodes();
            $response['ConfigSync']['settings']['system_host_id'] = $this->getHostid();
            $response['ConfigSync']['settings']['configsync_version'] = $this->getVersion();
        }
        return $response;
    }

    public function setAction()
    {
        $response = array("status" => "fail", "message" => "Invalid request");

        if ($this->request->isPost()) {
            $model_ConfigSync = new ConfigSync();
            $model_ConfigSync->setNodes($this->request->getPost('ConfigSync'));
            $response["validations"] = $this->unpackValidationMessages($model_ConfigSync, 'ConfigSync');

            if (0 == count($response["validations"])) {
                $model_ConfigSync->serializeToConfig();
                Config::getInstance()->save();
                $response["status"] = "success";
                $response["message"] = "Configuration saved.";
                unset($response["validations"]);
            }
        }
        return $response;
    }

    public function testAction()
    {
        $response = array("status" => "fail", "message" => "Invalid request");

        if ($this->request->isPost()) {
            $model_ConfigSync = new ConfigSync();
            $model_ConfigSync->setNodes($this->request->getPost('ConfigSync'));
            $response["validations"] = $this->unpackValidationMessages($model_ConfigSync, 'ConfigSync');

            if (0 == count($response["validations"])) {
                $data = $this->request->getPost('ConfigSync');
                $backend = new Backend();

                $configd_run = sprintf(
                    'configsync test_parameters --provider=%s --bucket=%s --endpoint=%s --path=%s --key-id=%s --key-secret=%s',
                    escapeshellarg($data['settings']['storage_provider_provider']),     # provider   [0]
                    escapeshellarg($data['settings']['storage_provider_bucket']),       # bucket     [1]
                    escapeshellarg($data['settings']['storage_provider_endpoint']),     # endpoint   [2]
                    escapeshellarg($data['settings']['storage_provider_path']),         # path       [3]
                    escapeshellarg($data['settings']['storage_provider_key_id']),       # key_id     [4]
                    escapeshellarg($data['settings']['storage_provider_key_secret'])    # key_secret [5]
                );

                $response = json_decode(trim($backend->configdRun($configd_run)), true);
                if (empty($response)) {
                    $response = array(
                        "status" => "fail",
                        "message" => "Error calling configsync test_parameters via configd"
                    );
                }
            } else {
                $response["message"] = "Invalid configuration data provided for testing";
            }
        }
        if (isset($response['data']) && isset($response['data'][0]) && isset($response['data'][0]["target_filename"])) {
            $response["message"] = $response["message"] . "/" . $response["data"][0]["target_filename"];
        }
        return $response;
    }

    private function getHostid()
    {
        if (file_exists('/etc/hostid')) {
            return trim(file_get_contents('/etc/hostid'));
        }
        return '00000000-0000-0000-0000-000000000000';
    }

    private function getVersion()
    {
        $backend = new Backend();
        $response = json_decode(trim($backend->configdRun("configsync get_version")), true);
        return $response["version"];
    }

    private function unpackValidationMessages($model, $namespace)
    {
        $response = array();
        $validation_messages = $model->performValidation();
        foreach ($validation_messages as $field => $message) {
            $response[$namespace . '.' . $message->getField()] = $message->getMessage();
        }
        return $response;
    }
}