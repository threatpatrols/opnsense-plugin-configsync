#!/bin/bash

set -e

remote=${1}
action=${2}

if [ -z ${remote} ] || [ -z ${action} ]; then
    echo 'usage: '$0' <host-address> <install|uninstall>'
    exit 1
fi

if ! [[ ${remote} = *"@"* ]]; then
    remote="root@${remote}"
fi

local_base_path=$(realpath $(dirname $0)/../../)
local_opnsense_base_path="${local_base_path}/src/opnsense"
remote_opnsense_base_path="/usr/local/opnsense"

local_opnsense_path=${local_opnsense_base_path}
remote_opnsense_path=${remote}:${remote_opnsense_base_path}

deploy_file()
{
    local src_file=${1}
    local dst_file=${2}
    echo "${src_file}"
    ssh $remote "mkdir -p \"\`dirname ${remote_opnsense_base_path}/${dst_file}\`\""
    rsync -a --no-o --no-g "${local_opnsense_path}/${src_file}" "${remote_opnsense_path}/${dst_file}"
}

dev_install()
{
    # deploy_files
    cd ${local_opnsense_path}
    for filename_find in $(find . -type f -not -name *.pyc); do
        filename=$(echo $filename_find | sed 's/^..//')
        deploy_file ${filename} ${filename}
    done

    # deploy_service
    rsync -a --no-o --no-g "${local_opnsense_path}/../etc/rc.d/configsync" "${remote}:/usr/local/etc/rc.d/configsync"
    rsync -a --no-o --no-g "${local_opnsense_path}/../etc/inc/plugins.inc.d/configsync.inc" "${remote}:/usr/local/etc/inc/plugins.inc.d/configsync.inc"

    # deploy_www
    rsync -a --no-o --no-g "${local_opnsense_path}/../www/diag_logs_configsync.php" "${remote}:/usr/local/www/diag_logs_configsync.php"

    ssh $remote "configctl template reload VerbNetworks/ConfigSync"
    ssh $remote "/usr/local/etc/rc.configure_plugins"

}

dev_uninstall()
{
    ssh $remote "configctl configsync stop"
    ssh $remote "rm -Rf /usr/local/opnsense/mvc/app/models/VerbNetworks"
    ssh $remote "rm -Rf /usr/local/opnsense/mvc/app/views/VerbNetworks"
    ssh $remote "rm -Rf /usr/local/opnsense/mvc/app/controllers/VerbNetworks"
    ssh $remote "rm -Rf /usr/local/opnsense/scripts/VerbNetworks"
    ssh $remote "rm -Rf /usr/local/opnsense/service/templates/VerbNetworks"
    ssh $remote "rm -Rf /usr/local/etc/configsync"
    ssh $remote "rm -Rf /var/db/configsync; rm -Rf /var/cache/configsync;"

    ssh $remote "rm -f /usr/local/opnsense/mvc/app/cache/*"

    ssh $remote "rm -f /usr/local/etc/rc.d/configsync"
    ssh $remote "rm -f /usr/local/etc/inc/plugins.inc.d/configsync.inc"
    ssh $remote "rm -f /usr/local/www/diag_logs_configsync.php"
    ssh $remote "rm -f /usr/local/opnsense/service/conf/actions.d/actions_configsync.conf"
    ssh $remote "rm -f /var/log/configsync.log"
    ssh $remote "rm -f /usr/local/opnsense/version/configsync"

    ssh $remote "/usr/local/etc/rc.configure_plugins"
}


if [ $action = "install" ]; then
    dev_install
elif [ $action = "uninstall" ]; then
    dev_uninstall
fi
