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
                    Configuration Sync (configsync) is an OPNsense plugin designed to one-way
                    synchronize the OPNsense system configuration <code>.xml</code>code> files to an (S3
                    compatible) cloud-storage provider.  Actions for configsync are triggered
                    by an OPNsense syshook-config event.
                </p>

                <p>
                    Configuration Sync is well-suited to DevOps automation arrangements where OPNsense
                    instances need to be re-invoked with a previously existing configuration.
                </p>

                <p>
                    Configuration Sync happens to be a great OPNsense configuration backup solution when
                    used by itself.
                </p>

                <p>Configuration Sync supports the following cloud storage providers:</p>
                <ul>
                    <li>Amazon Web Services - S3</li>
                    <li>Google - Cloud Storage</li>
                    <li>Digital Ocean - Spaces</li>
                    <li>Other - S3 compatible endpoints</li>
                </ul>

                <p>
                    Configuration Sync uses the well known Python Boto3 library to achieve generic S3
                    connectivity; if Boto3 can handle the S3 storage provider you should be able to use it here.
                </p>

                <p>
                Please refer to the online documentation for the latest storage-provider configuration detail.
                <br>
                <a rel="noreferrer noopener" target="_blank" href="https://documentation.threatpatrols.com/opnsense/plugins/">https://documentation.threatpatrols.com/opnsense/plugins</a>
                </p>

                <h2>Metadata</h2>
                <p>
                    Each OPNsense <code>.xml</code> file object written by Configuration Sync adds extra meta-data
                    to the stored file-object that helps confirm the OPNsense instance the file originated from.
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
                    These values are helpful in filtering and selecting specific configuration files from the
                    storage-provider bucket at a later time.
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
