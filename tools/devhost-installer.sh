#!/bin/bash

#
#    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
#    All rights reserved.
#
#    Distributed under the Parity Public License, Version 7.0.0
#    https://paritylicense.com/versions/7.0.0
#

set -e

remote_address=${1}
remote_default_user="root"
action=${2}

if [ -z "${remote_address}" ] || [ -z "${action}" ]; then
    echo 'usage: '${0}' <remote-user@remote-host|remote-host> <install|uninstall>'
    exit 1
fi

if [[ ${remote_address} = *"@"* ]]; then
    remote="${remote_address}"
else
    remote="${remote_default_user}@${remote_address}"
fi

ssh_options="-o ControlMaster=auto -o ControlPersist=60s -q"
local_base_path=$(realpath $(dirname ${0})/../src/)
remote_base_path="/usr/local"

# =============================================================================

echo
echo "Variable settings"
echo "==="
echo "remote:                 ${remote}"
echo "action:                 ${action}"
echo "ssh_options:            ${ssh_options}"
echo "local_base_path:        ${local_base_path}"
echo "remote_base_path:       ${remote_base_path}"
echo

# =============================================================================

dev_install()
{
  # Install boto3 if not yet installed
  remote_py_version=$(ssh ${ssh_options} ${remote} "ls -1 /usr/local/lib | grep ^python | head -n1 | tr -d 'thon.'")
  if [[ $(ssh ${ssh_options} ${remote} "pkg info | grep -c ${remote_py_version}-boto3") -eq 0 ]]; then
    echo "Installing ${remote_py_version}-boto3"
    echo "==="
    ssh ${ssh_options} ${remote} "pkg install -y ${remote_py_version}-boto3"
    echo
  fi

  # deploy_files
  echo "Deploy configsync files"
  echo "==="
  cd "${local_base_path}"
  for filepath_find in $(find . -type f -not -path */.py* -not -name *.pyc -not -name test_* -not -name .git*); do
      filepath=$(echo $filepath_find | sed 's/^..//')
      deploy_file "${local_base_path}/${filepath}" "${remote_base_path}/${filepath}"
  done
  echo

  echo "Rebuild the ConfigSync templates"
  echo "==="
  ssh ${ssh_options} ${remote} "configctl template reload ThreatPatrols/ConfigSync"
  echo

  echo "Restart OPNsense configd"
  echo "==="
  ssh ${ssh_options} ${remote} "/usr/local/etc/rc.configure_plugins; service configd restart"
  echo
}

# =============================================================================

dev_uninstall()
{
  echo "Remove configsync files"
  echo "==="
  cd "${local_base_path}"
  for filepath_find in $(find . -type f -not -path */.py* -not -name *.pyc -not -name test_* -not -name .git*); do
      filepath=$(echo $filepath_find | sed 's/^..//')
      remove_file "${remote_base_path}/${filepath}"
  done
  echo

  echo "Restart OPNsense configd"
  echo "==="
  ssh ${ssh_options} ${remote} "/usr/local/etc/rc.configure_plugins; service configd restart"
  echo
}

# =============================================================================

deploy_file()
{
  local src_fullpath=${1}
  local dst_fullpath=${2}
  echo "deploy: ${src_fullpath/${local_base_path}\//\{base\}/}"
  ssh ${ssh_options} "${remote}" "mkdir -p \"\`dirname ${dst_fullpath}\`\""
  scp ${ssh_options} -p "${src_fullpath}" "${remote}:${dst_fullpath}"
}

# =============================================================================

remove_file()
{
    local dst_fullpath=${1}
    if [[ "${dst_fullpath}" == *"ConfigSync"* ]]; then
      echo "remove-path: ${dst_fullpath}"
      ssh ${ssh_options} "${remote}" "rm -Rf \"\`dirname ${dst_fullpath}\`\""
    else
      echo "remove-file: ${dst_fullpath}"
      ssh ${ssh_options} "${remote}" "rm -f ${dst_fullpath}"
    fi
}

# =============================================================================

if [[ "${action}" = "install" ]]; then
    dev_install
    exit 0
elif [[ "${action}" = "uninstall" ]]; then
    dev_uninstall
    exit 0
fi

echo "ERROR: unknown action"
exit 1
