# Configuration Sync for OPNsense
Configuration Sync (configsync) is an OPNsense plugin designed to one-way 
synchronize the OPNsense system configuration `.xml` files to an (S3 
compatible) cloud-storage provider.  The `configsync` actions are triggered 
by OPNsense configuration save events.

Configuration Sync supports the following cloud storage providers:-
* Amazon Web Services - S3
* Google - Cloud Storage
* Digital Ocean - Spaces
* Other - S3 compatible endpoints

Configuration Sync works well on OPNsense systems with MultiCLOUDsense&trade; in 
conjunction with DevOps tools like Terraform or Ansible to achieve instance 
automation to create, destroy and re-create OPNsense instances with the 
same system configuration.

The ability to manage OPNsense instances using DevOps automation tooling 
means OPNsense becomes a first-class choice for building and managing 
multi-cloud or other hybrid network infrastructure arrangements.

Configuration Sync also happens to be a great OPNsense configuration backup 
solution when used by itself. 

## Documentation
* https://documentation.threatpatrols.com/opnsense/plugins

## Installation
Installation is possible via the Threat Patrols plugin and package repo:-
* https://repo.threatpatrols.com

Refer to the documentation for details on adding this repo to your OPNsense instance:-
* https://documentation.threatpatrols.com/opnsense/repo

## Source
For plugin development, checkout the source repo
* https://github.com/threatpatrols/opnsense-plugin-configsync

## Copyright
* Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
* Copyright (c) 2018 Verb Networks Pty Ltd <contact@verbnetworks.com>
* Copyright (c) 2018 Nicholas de Jong <me@nicholasdejong.com>

All rights reserved.

## License
Distributed under the Parity Public License, Version 7.0.0
https://paritylicense.com/versions/7.0.0
