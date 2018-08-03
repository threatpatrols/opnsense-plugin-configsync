#!/bin/bash

remote=${1}
action=${2}

if [ -z ${remote} ] || [ -z ${action} ]; then
    echo 'usage: '$0' <host-address> <install|remove>'
    exit 1
fi

if ! [[ ${remote} = *"@"* ]]; then
    remote="root@${remote}"
fi

local_base_path=$(realpath $(dirname $0)/../)
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

remove_file()
{
    local dst_file=${1}
    ssh $remote "rm \"${remote_opnsense_base_path}/${dst_file}\""
}

configure_plugins()
{
    ssh $remote "/usr/local/etc/rc.configure_plugins"
}

reload_config()
{
    ssh $remote "configctl template reload VerbNetworks/ConfigSync"
}

deploy_service()
{
    rsync -a --no-o --no-g "${local_opnsense_path}/../bin/configsync-monitord" "${remote}:/usr/local/sbin/configsync-monitord"
    rsync -a --no-o --no-g "${local_opnsense_path}/../etc/rc.d/configsync" "${remote}:/usr/local/etc/rc.d/configsync"
    rsync -a --no-o --no-g "${local_opnsense_path}/../etc/inc/plugins.inc.d/configsync.inc" "${remote}:/usr/local/etc/inc/plugins.inc.d/configsync.inc"
}

cd ${local_opnsense_path}
for filename_find in $(find . -type f -not -name *.pyc); do
    filename=$(echo $filename_find | sed 's/^..//')
    if [ $action = "remove" ]; then
        remove_file ${filename}
    else
        deploy_file ${filename} ${filename}
    fi
done

configure_plugins
reload_config
deploy_service
