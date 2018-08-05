#!/bin/bash

remote_host=${1}
remote_user=root

plugin_path='net-mgmt/configsync'
local_base_path=$(realpath $(dirname $(realpath $0))/../../../opnsense-plugins)
remote_base_path=/root/opnsense-plugins

if [ -z ${remote_host} ]; then
    echo 'usage: '$0' <host-address>'
    exit 1
fi

# push the code to the remote FreeBSD system
rsync \
    -rv \
    --copy-links \
    --delete \
    --exclude .git \
    --exclude work \
    --exclude package \
    ${local_base_path}/ \
    $remote_user@$remote_host:${remote_base_path}

## do the build
ssh $remote_user@$remote_host "cd ${remote_base_path}/${plugin_path}; rm -Rf work; make clean; make package"

## pull the .txz packages back
rsync \
    --ignore-existing \
    $remote_user@$remote_host:${remote_base_path}/${plugin_path}/work/pkg/*.txz \
    $(realpath $(dirname $(realpath $0))/../../package)

## re-roll the SHA256SUMS
cd $(realpath $(dirname $(realpath $0))/../../package)
sha256sum *.txz > SHA256SUMS
