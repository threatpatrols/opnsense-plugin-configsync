<?php
namespace VerbNetworks\ConfigSync;

class IndexController extends \OPNsense\Base\IndexController
{
    public function indexAction()
    {
        $this->view->pick('VerbNetworks/ConfigSync/index');
    }
}
