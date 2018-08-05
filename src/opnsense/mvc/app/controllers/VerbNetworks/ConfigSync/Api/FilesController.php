<?php

# Copyright (c) 2018 Verb Networks Pty Ltd <contact [at] verbnetworks.com>
#  - All rights reserved.
#
# Apache License v2.0
#  - http://www.apache.org/licenses/LICENSE-2.0

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
