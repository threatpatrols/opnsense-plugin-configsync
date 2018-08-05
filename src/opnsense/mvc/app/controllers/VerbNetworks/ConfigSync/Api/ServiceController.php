<?php

namespace VerbNetworks\ConfigSync\Api;

use \OPNsense\Base\ApiControllerBase;
use \OPNsense\Core\Backend;

class ServiceController extends ApiControllerBase
{
    
    public function reloadAction()
    {
        $response = array("status"=>"fail", "message" => "Invalid request");

        if ($this->request->isPost()) {
            $backend = new Backend();
            $backend_result = trim($backend->configdRun('template reload VerbNetworks/ConfigSync'));
            if (strtoupper($backend_result) == "OK") {
                $response = array("status"=>"success", "message" => "Template reload okay");
            }
        }
        
        return $response;
    }

    public function statusAction()
    {
        $response = array("status"=>"fail", "message" => "Invalid request");

        if ($this->request->isPost()) {
            $backend = new Backend();
            $backend_result = trim($backend->configdRun('configsync status'));
            if (FALSE === strpos(strtolower($backend_result),' not running')) {
                $response = array("status"=>"running");
            } else {
                $response = array("status"=>"stopped");
            }
        }

        return $response;
    }

    public function startAction()
    {
        $response = array("status"=>"fail", "message" => "Invalid request");

        if ($this->request->isPost()) {
            $backend = new Backend();
            $backend_result = trim($backend->configdRun('configsync start'));
            if (strtoupper($backend_result) == "OK") {
                $response = array("status"=>"success", "message" => "ConfigSync service started");
            }
        }
        
        return $response;
    }

    public function restartAction()
    {
        $response = array("status"=>"fail", "message" => "Invalid request");

        if ($this->request->isPost()) {
            $backend = new Backend();
            $backend_result = trim($backend->configdRun('configsync restart'));
            if (strtoupper($backend_result) == "OK") {
                $response = array("status"=>"success", "message" => "ConfigSync service stopped");
            }
        }
        
        return $response;
    }
    
    public function stopAction()
    {
        $response = array("status"=>"fail", "message" => "Invalid request");

        if ($this->request->isPost()) {
            $backend = new Backend();
            $backend_result = trim($backend->configdRun('configsync stop'));
            if (strtoupper($backend_result) == "OK") {
                $response = array("status"=>"success", "message" => "ConfigSync service stopped");
            }
        }
        
        return $response;
    }

}
