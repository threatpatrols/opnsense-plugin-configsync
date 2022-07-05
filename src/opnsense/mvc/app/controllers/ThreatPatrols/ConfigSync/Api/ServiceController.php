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

use OPNsense\Base\ApiControllerBase;
use OPNsense\Core\Backend;

class ServiceController extends ApiControllerBase
{
    public function reloadAction()
    {
        $response = array("status" => "fail", "message" => "Invalid request");

        if ($this->request->isPost()) {
            $backend = new Backend();
            $backend_result = trim($backend->configdRun('template reload ThreatPatrols/ConfigSync'));
            if (true === strpos($backend_result, 'OK')) {
                $response = array("status" => "success", "message" => "Template reload okay");
            }
        }
        return $response;
    }

    public function statusAction()
    {
        return array();
    }

    public function startAction()
    {
        return array();
    }

    public function restartAction()
    {
        return array();
    }

    public function stopAction()
    {
        return array();
    }
}
