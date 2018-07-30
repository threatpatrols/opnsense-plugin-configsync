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
            <div class="col-md-12">
                <p>Content about this plugin</p>
                <hr />
            </div>
        </div>
    </div>
</div>

<style>
    #configsync\.settings\.StorageFullURI, #configsync\.settings\.SystemHostid {
        line-height: 34px;
        display: inline-block;
        vertical-align: middle;
        
        font-size: 80%;
        font-family: Menlo, Monaco, Consolas, "Courier New", monospace;
    }
</style>

<script>
    $(document).ready(function() {
        
        function update_fulluri() {
            if($('#configsync\\.settings\\.Provider').val() === 'awss3') {
                var link_url = 'https://s3.console.aws.amazon.com/s3/buckets/';
                link_url += $('#configsync\\.settings\\.StorageBucket').val() + '/';
                link_url += $('#configsync\\.settings\\.StoragePath').val() + '/';
                
                var link_name = 's3://';
                link_name += $('#configsync\\.settings\\.StorageBucket').val() + '/';
                link_name += $('#configsync\\.settings\\.StoragePath').val();
            }
            $('#configsync\\.settings\\.StorageProviderLink').html('<a target="_blank" href="' + link_url +'">' + link_name + '</a>');
        }
        
        $("#configsync\\.settings\\.StorageBucket").change(function(){
            update_fulluri();
        });
        
        $("#configsync\\.settings\\.StoragePath").change(function(){
            update_fulluri();
        });
        
        mapDataToFormUI({frm_Settings:"/api/configsync/settings/get"}).done(function(data){
            formatTokenizersUI();
            $('.selectpicker').selectpicker('refresh');
            update_fulluri();
        });

        $("#saveAction").click(function(){
            $("#responseMsg").removeClass("hidden").removeClass("alert-danger").addClass('alert-info').html("Saving settings...");
            saveFormToEndpoint(url="/api/configsync/settings/set", formid='frm_Settings', callback_ok=function(){
                $("#responseMsg").html("Configuration Sync service settings saved.");
                ajaxCall(url="/api/configsync/service/reload", sendData={},callback=function(data, status) {
                    $("#responseMsg").html("Configuration Sync service settings saved and reloaded.");
                });
            });
        });
        
        $("#testAction").click(function(){
            $("#responseMsg").removeClass("hidden").removeClass("alert-danger").addClass('alert-info').html("Running tests...");
            saveFormToEndpoint(url="/api/configsync/settings/test", formid='frm_Settings', callback_ok=function(data){
                if(data['status'] != 'success') {
                    $("#responseMsg").removeClass("alert-info").addClass('alert-danger');
                }
                $("#responseMsg").html(data['message']);
            });
        });

    });
</script>
