<?php
namespace VerbNetworks\ConfigSync;

class AboutController extends \OPNsense\Base\IndexController
{
    public function indexAction()
    {
        $this->view->pick('VerbNetworks/ConfigSync/about');
    }
}
