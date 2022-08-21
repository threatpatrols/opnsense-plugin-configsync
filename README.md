# Configuration Sync (configsync) for OPNsense

Configuration Sync (configsync) is an OPNsense plugin designed to one-way 
synchronize the OPNsense system configuration `.xml` files to an (S3 compatible) 
cloud-storage provider.  Actions for `configsync` are automatically triggered 
by an OPNsense syshook-config event.

Configuration Sync is well-suited to DevOps automation arrangements where OPNsense
instances are re-invoked with a previously existing configuration.

Configuration Sync also happens to be a great OPNsense configuration backup solution 
when used by itself.

Configuration Sync supports the following cloud storage providers:-

 * Amazon Web Services - S3
 * Google - Cloud Storage
 * Digital Ocean - Spaces
 * Other - S3 compatible endpoints

## Documentation
 * https://documentation.threatpatrols.com/opnsense/plugins/configsync/

## Issues
 * https://github.com/threatpatrols/opnsense-plugin-configsync/issues

## Source
 * https://github.com/threatpatrols/opnsense-plugin-configsync

## Copyright
* Copyright &copy; 2022 Threat Patrols Pty Ltd &lt;contact@threatpatrols.com&gt;
* Copyright &copy; 2018 Verb Networks Pty Ltd &lt;contact@verbnetworks.com&gt;
* Copyright &copy; 2018 Nicholas de Jong &lt;me@nicholasdejong.com&gt;

All rights reserved.

## License
* BSD-2-Clause - see LICENSE file for full details.
