<?php
namespace VerbNetworks\ConfigSync;

class FilesController extends \OPNsense\Base\IndexController
{
    public function indexAction()
    {
        $this->view->pick('VerbNetworks/ConfigSync/files');
    }
}
