<?php
namespace VerbNetworks\ConfigSync;

use \OPNsense\Core\Config;

class ControllerUtils
{
    
    public static function getHostid() {
        $hostid = '00000000-0000-0000-0000-000000000000';
        if(file_exists('/etc/hostid')) {
            $hostid = trim(file_get_contents('/etc/hostid'));
        }
        return $hostid;
    }
    
    public static function getHostname(){
        $cnf = Config::getInstance();
        return strtolower($cnf->object()->system->hostname);
    }
    
    public static function packData($data) {
        return base64_encode(gzcompress(json_encode($data), 9));
    }
    
    public static function unpackData($data) {
        json_decode(gzuncompress(base64_decode($data)));
    }
    
    public static function unpackValidationMessages($model, $namespace) {
        $response = array();
        $validation_messages = $model->performValidation();
        foreach ($validation_messages as $field => $message) {
            $response[$namespace.'.'.$message->getField()] = $message->getMessage();
        }
        return $response;
    }
}
