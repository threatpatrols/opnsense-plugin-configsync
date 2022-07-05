{#
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    Copyright (c) 2018 Verb Networks Pty Ltd <contact@verbnetworks.com>
    Copyright (c) 2018 Nicholas de Jong <me@nicholasdejong.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
#}

<div class="alert alert-info hidden" role="alert" id="responseMsg"></div>

<ul class="nav nav-tabs" data-tabs="tabs" id="maintabs">
    <li class="active"><a data-toggle="tab" href="#settings">{{ lang._('Settings') }}</a></li>
    <li><a data-toggle="tab" href="#about">{{ lang._('About') }}</a></li>
</ul>

<div class="tab-content content-box tab-content">
    <div id="settings" class="tab-pane fade in active">
        <div class="content-box" style="padding-bottom: 1.5em;">
            {{ partial("layout_partials/base_form",['fields':settingsForm,'id':'frm_Settings'])}}
            <div class="col-md-12">
                <hr />
                <button class="btn btn-primary" id="saveAction" type="button"><b>{{ lang._('Save') }}</b> <i id="saveAct_progress"></i></button>
                <button class="btn btn-primary"  id="testAction" type="button"><b>{{ lang._('Test Credentials') }}</b></button>
            </div>
        </div>
    </div>
    <div id="about" class="tab-pane fade in">
        <div class="content-box" style="padding-bottom: 1.5em;">

            <div  class="col-md-12">
                <h1>Configuration Sync</h1>
                <p>
                    Configuration Sync (configsync) is an OPNsense plugin designed to synchronize
                    the OPNsense system configuration <code>.xml</code> files to an (S3
                    compatible) cloud-storage provider.  The configsync action is triggered by
                    OPNsense configuration save events.
                </p>

                <p>Configuration Sync supports the following cloud storage providers:</p>
                <ul>
                    <li>Amazon - S3</li>
                    <li>Google - Cloud Storage</li>
                    <li>Digital Ocean - Spaces</li>
                    <li>Other - S3 compatible endpoints</li>
                </ul>

                <p>
                    Configuration Sync works well on OPNsense systems with MultiCLOUDsense&trade;
                    in conjunction with DevOps tools like Terraform or Ansible to achieve
                    instance automation to create, destroy and re-create OPNsense instances with
                    the same system configuration.
                </p>

                <p>
                    The ability to manage OPNsense instances using DevOps automation tooling
                    means OPNsense becomes a first-class choice for building and managing
                    multi-cloud or other hybrid network infrastructure arrangements.
                </p>

                <p>
                    Configuration Sync also happens to be a great OPNsense configuration backup
                    solution when used by itself.
                </p>

                <h2>Stored Configurations</h2>
                <p>
                    Configuration Sync is designed to <strong>not</strong> require (or provide)
                    any read access to the files written to the storage provider.  This means
                    policies can be applied to the associated account API credentials that are
                    limited to put-object and list-bucket permissions.  This in turn means the
                    risks of API credential exposure are nicely limited.
                </p>
                
                <h2>Example AWS IAM policy</h1>
                <p>
                    Consider the following AWS IAM policy below to restrict the resources and
                    actions available to the AWS account associated with the API credentials
                    used.  Of particular note is that the policy does not require <code>GetObject</code>
                    permissions.
                </p>
<pre>{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [ "s3:ListBucket" ],
            "Resource": [ "arn:aws:s3:::BUCKET_NAME" ]
        },
        {
            "Effect": "Allow",
            "Action": [ "s3:ListBucket", "s3:PutObject" ],
            "Resource": [ "arn:aws:s3:::BUCKET_NAME/PATH_NAME/*" ]
        }
    ]
}</pre>
                <p>
                    <strong>Note:</strong> Be sure to replace <code>BUCKET_NAME</code> and <code>PATH_NAME</code>
                    values with your own values above.
                </p>

                <p>
                    Similar policy arrangements are possible with other storage providers depending on the
                    ACL functionality of the storage provider.
                </p>

                <h2>Metadata</h2>
                <p>
                    The OPNsense <code>.xml</code> configuration files written to the storage provider
                    also have additional metadata attached to them by configsync.
                </p>

                <p>Metadata fields</p>
                <ul>
                    <li><code>filetype</code> - always "opnsense-config"</li>
                    <li><code>mtime</code> - the last modified timestamp of the OPNsense config file</li>
                    <li><code>bytes</code> - the file size in bytes of the OPNsense config file</li>
                    <li><code>md5</code> - the md5-digest of the OPNsense config file</li>
                    <li><code>hostid</code> - the unique host-id of the OPNsense system</li>
                    <li><code>hostname</code> - the hostname of the OPNsense system</li>
                </ul>

                <p>
                    These values may be used to filter and select specific configuration files from
                    the storage-provider bucket at a later time.
                </p>

                <hr />
                
                <h1>Additional Documentation</h1>
                <ul>
                    <li><a rel="noreferrer noopener" target="_blank" href="https://documentation.threatpatrols.com/opnsense/plugins/">https://documentation.threatpatrols.com/opnsense/plugins</a></li>
                </ul>

                <h1>Copyright</h1>
                <ul>
                    <li><a rel="noreferrer noopener" target="_blank" href="https://github.com/threatpatrols/opnsense-plugin-configsync">Configuration Sync</a> (c) 2022 <a rel="noreferrer noopener" target="_blank" href="https://www.threatpatrols.com">Threat Patrols Pty Ltd</a></li>
                </ul>

                <h1>License</h1>
                <p>Distributed under the <a rel="noreferrer noopener" target="_blank" href="https://paritylicense.com/versions/7.0.0">Parity Public License, Version 7.0.0</a></p>
                <p></p>

            </div>
        </div>
    </div>
</div>

<style>
    #ConfigSync\.settings\.system_host_id, #ConfigSync\.settings\.configsync_version {
        line-height: 34px;
        display: inline-block;
        vertical-align: middle;
        font-size: 80%;
        font-family: Menlo, Monaco, Consolas, "Courier New", monospace;
    }
</style>

<script>

    $(document).ready(function() {

        updateServiceControlUI('configsync');

        mapDataToFormUI({frm_Settings:"/api/configsync/settings/get"}).done(function(data){
            formatTokenizersUI();
            $('.selectpicker').selectpicker('refresh');
        });

        $("#testAction").click(function(){
            $("#responseMsg").removeClass("hidden").removeClass("alert-danger").addClass('alert-info').html("{{ lang._('Running tests') }}...");
            saveFormToEndpoint(
                url = '/api/configsync/settings/test',
                formid ='frm_Settings',
                callback_ok = function(data){
                    if(data['status'] !== 'success') {
                        $("#responseMsg").removeClass("alert-info").addClass('alert-danger');
                    }
                    $("#responseMsg").html(data['message']);
                },
                disable_dialog = true
            );
        });

        $("#saveAction").click(function(){
            $("#responseMsg").removeClass("hidden").removeClass("alert-danger").addClass('alert-info').html("{{ lang._('Saving settings') }}...");
            saveFormToEndpoint(
                url = '/api/configsync/settings/set',
                formid = 'frm_Settings',
                callback_ok = function(){
                    $("#responseMsg").html("{{ lang._('Configuration Sync service settings saved') }}.");
                    ajaxCall(url = "/api/configsync/service/reload", sendData = {}, callback = function(data, status) {
                        $("#responseMsg").html("{{ lang._('Configuration Sync service settings saved and reloaded') }}.");
                        ajaxCall(url = "/api/configsync/service/restart", sendData = {}, callback = function(data, status) {
                            updateServiceControlUI('configsync');
                        });
                    });
                },
                disable_dialog = true
            );
            updateServiceControlUI('configsync');
        });
    });
</script>
