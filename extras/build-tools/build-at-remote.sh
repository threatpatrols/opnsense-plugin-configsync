#!/bin/bash

set -e

remote_host=${1}
remote_user=root

opnsense_plugins_repo_path=$(realpath $(dirname $(realpath $0))/../../../opnsense-plugins)
configsync_plugin_repo_path=$(realpath $(dirname $(realpath $0))/../../)
configsync_opnsense_plugins_subpath='net-mgmt/configsync'
remote_base_path='/root/opnsense-plugins'

if [ -z ${remote_host} ]; then
    echo 'usage: '$0' <host-address>'
    exit 1
fi

# echo some helpful output
echo ""
echo "remote:                               ${remote_user}@${remote_host}"
echo "remote_base_path:                     ${remote_base_path}"
echo "opnsense_plugins_repo_path:           ${opnsense_plugins_repo_path}"
echo "configsync_plugin_repo_path:          ${configsync_plugin_repo_path}"
echo "configsync_opnsense_plugins_subpath:  ${configsync_opnsense_plugins_subpath}"
echo ""

# copy into place the material to be injected into the repo
rm -Rf ${opnsense_plugins_repo_path}/${configsync_opnsense_plugins_subpath}
mkdir ${opnsense_plugins_repo_path}/${configsync_opnsense_plugins_subpath}
rsync --exclude *.pyc -ra ${configsync_plugin_repo_path}/src/ ${opnsense_plugins_repo_path}/${configsync_opnsense_plugins_subpath}/src/
rsync -a ${configsync_plugin_repo_path}/LICENSE ${opnsense_plugins_repo_path}/${configsync_opnsense_plugins_subpath}/LICENSE
rsync -a ${configsync_plugin_repo_path}/Makefile ${opnsense_plugins_repo_path}/${configsync_opnsense_plugins_subpath}/Makefile
rsync -a ${configsync_plugin_repo_path}/pkg-descr ${opnsense_plugins_repo_path}/${configsync_opnsense_plugins_subpath}/pkg-descr
rsync -a ${configsync_plugin_repo_path}/README.md ${opnsense_plugins_repo_path}/${configsync_opnsense_plugins_subpath}/README.md

# push the local opnsense_plugins_repo to the remote FreeBSD system
echo rsync \
    --recursive \
    --copy-links \
    --delete \
    ${opnsense_plugins_repo_path}/ \
    ${remote_user}@${remote_host}:${remote_base_path}

## lint
ssh ${remote_user}@${remote_host} "cd ${remote_base_path}/${configsync_opnsense_plugins_subpath}; make lint"

## style
ssh ${remote_user}@${remote_host} "cd ${remote_base_path}/${configsync_opnsense_plugins_subpath}; make style"

## do the build
ssh ${remote_user}@${remote_host} "cd ${remote_base_path}/${configsync_opnsense_plugins_subpath}; make package"

## pull the .txz packages back
rsync \
    --ignore-existing \
    ${remote_user}@${remote_host}:${remote_base_path}/${configsync_opnsense_plugins_subpath}/work/pkg/*.txz \
    ${configsync_plugin_repo_path}/package

## re-roll the SHA256SUMS
cd ${configsync_plugin_repo_path}/package
sha256sum *.txz > SHA256SUMS
