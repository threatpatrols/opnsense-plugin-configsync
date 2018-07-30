<?php
namespace VerbNetworks\ConfigSync;

class LogfileController extends \OPNsense\Base\IndexController
{
    public function indexAction()
    {
        $this->view->pick('VerbNetworks/ConfigSync/logfile');
    }
}
