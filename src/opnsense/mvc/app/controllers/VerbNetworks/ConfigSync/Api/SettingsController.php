<?php
namespace VerbNetworks\ConfigSync\Api;

use \OPNsense\Core\Backend;
use \OPNsense\Core\Config;
use \OPNsense\Base\ApiControllerBase;
use \VerbNetworks\ConfigSync\ConfigSync;
use \VerbNetworks\ConfigSync\ControllerUtils;

class SettingsController extends ApiControllerBase
{
    
    public function getAction()
    {
        $response = array();
        if ($this->request->isGet()) {
            $model_ConfigSync = new ConfigSync();
            $response['configsync'] = $model_ConfigSync->getNodes();
            $response['configsync']['settings']['SystemHostid'] = ControllerUtils::getHostid();
        }
        return $response;
    }

    public function setAction()
    {
        $response = array("status"=>"fail", "message" => "Invalid request");
        
        if ($this->request->isPost()) {
            
            $model_ConfigSync = new ConfigSync();
            $model_ConfigSync->setNodes($this->request->getPost("configsync"));
            $response["validations"] = ControllerUtils::unpackValidationMessages($model_ConfigSync, 'configsync');
            
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
        $response = array("status"=>"fail", "message" => "Invalid request");
        
        if ($this->request->isPost()) {
            
            $model_ConfigSync = new ConfigSync();
            $model_ConfigSync->setNodes($this->request->getPost("configsync"));
            $response["validations"] = ControllerUtils::unpackValidationMessages($model_ConfigSync, 'configsync');
            
            if (0 == count($response["validations"])) {

                $data = $this->request->getPost("configsync");
                $backend = new Backend();
                
                if('awss3' == $data['settings']['Provider']) {
                    $configd_run = sprintf(
                            "configsync aws_test_parameters %s %s %s %s", 
                            $data['settings']['ProviderKey'],
                            $data['settings']['ProviderSecret'],
                            $data['settings']['StorageBucket'],
                            $data['settings']['StoragePath']
                            );
                    $response = json_decode(trim($backend->configdRun($configd_run)), true);
                }
                else {
                    $response["message"] = "Provider not supported";
                }
            }
            else {
                $response["message"] = "Invalid configuration data provided for testing";
            }
        }
        
        if (isset($response['data'])) {
            if (is_string($response["data"])) {
                $response["message"] = $response["message"] . ": " . $response["data"];
            } else {
                $response["message"] = $response["message"] . ": " . json_encode($response["data"]);
            }
        }
        
        return $response;
    }
    
}
