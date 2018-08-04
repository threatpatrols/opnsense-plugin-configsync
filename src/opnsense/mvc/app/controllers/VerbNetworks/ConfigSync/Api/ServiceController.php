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

}
