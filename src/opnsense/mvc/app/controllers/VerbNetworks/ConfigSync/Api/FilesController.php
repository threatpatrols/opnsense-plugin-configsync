<?php

namespace VerbNetworks\ConfigSync\Api;

use \OPNsense\Base\ApiControllerBase;
use \OPNsense\Core\Backend;

class FilesController extends ApiControllerBase
{
    
    public function getAction()
    {
        $response = array("status"=>"fail", "message" => "Invalid request");

        if ($this->request->isGet()) {
            $backend = new Backend();
            $response = json_decode(trim($backend->configdRun(
                    "configsync awss3_get_file_list"
            )), true);
        }
        
        return $response;
    }
    
}
