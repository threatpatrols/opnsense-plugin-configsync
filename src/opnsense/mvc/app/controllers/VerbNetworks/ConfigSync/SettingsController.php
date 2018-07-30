<?php
namespace VerbNetworks\ConfigSync;

use \VerbNetworks\ConfigSync\ControllerUtils;

class SettingsController extends \OPNsense\Base\IndexController
{
    public function indexAction()
    {
        $this->view->pick('VerbNetworks/ConfigSync/settings');
        $this->view->settingsForm = $this->getForm("settings");
    }
}