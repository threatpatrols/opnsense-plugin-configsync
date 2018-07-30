<?php

namespace VerbNetworks\ConfigSync\Api;

use \OPNsense\Base\ApiControllerBase;
use \OPNsense\Core\Backend;

class ServiceController extends ApiControllerBase
{
    
    public function reloadAction()
    {
        $status = "failed";
        if ($this->request->isPost()) {
            $backend = new Backend();
            $backend_result = trim($backend->configdRun('template reload VerbNetworks/ConfigSync'));
            if (strtoupper($backend_result) == "OK") {
                $status = "ok";
            }
        }
        return array("status" => $status);
    }

}
