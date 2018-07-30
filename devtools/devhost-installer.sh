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
    rsync -a "${local_opnsense_path}/${src_file}" "${remote_opnsense_path}/${dst_file}"
}

remove_file()
{
    local dst_file=${1}
    ssh $remote "rm \"${remote_opnsense_base_path}/${dst_file}\""
}

configure_plugins()
{
    ssh $remote "/usr/local/etc/rc.configure_plugins"
    
    # service configd restart
    # configctl template reload VerbNetworks/ConfigSync
}

cd ${local_opnsense_path}
for filename_find in $(find . -type f -not -name *.pyc); do
    filename=$(echo $filename_find | sed 's/^..//')
    if [ $action = "install" ]; then
        deploy_file ${filename} ${filename}
    else
        remove_file ${filename}
    fi
done

configure_plugins
