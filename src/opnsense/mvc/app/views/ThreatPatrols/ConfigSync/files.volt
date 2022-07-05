{#
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    Copyright (c) 2018 Verb Networks Pty Ltd <contact@verbnetworks.com>
    Copyright (c) 2018 Nicholas de Jong <me@nicholasdejong.com>
    All rights reserved.

    Distributed under the Parity Public License, Version 7.0.0
    https://paritylicense.com/versions/7.0.0
#}

<script>
    
    function updateGridFilesTable() {
    
        $("#grid-files").UIBootgrid(
            {   search:'/api/configsync/files/list',
                options:{
                    rowCount:[10, 25, 100, -1] ,
                    ajax: true,
                    url: "/api/configsync/files/list",
                },                
            },
        );    
    }

    $(document).ready(function() {
        updateServiceControlUI('configsync');
        updateGridFilesTable();
    });

</script>

<div class="container-fluid">
    <div class="row">
        <div class="alert alert-info hidden" role="alert" id="responseMsg"></div>
    </div>
    <div class="row">
        <div class="col-md-12" id="content">
            
            <table id="grid-files" class="table table-condensed table-hover table-striped table-responsive">
                <thead>
                <tr>
                    <th data-column-id="timestamp_created" data-width="14em" data-type="string" data-sortable="true" data-visible="true">{{ lang._('Filename Timestamp') }}</th>
                    <th data-column-id="timestamp_synced" data-width="14em" data-type="string" data-sortable="true" data-visible="true">{{ lang._('Storage Timestamp') }}</th>
                    <th data-column-id="path" data-type="string" data-sortable="true" data-visible="true">{{ lang._('Storage Provider Path') }}</th>
                    <th data-column-id="storage_size" data-width="8em" data-type="string" data-sortable="true" data-visible="true">{{ lang._('Storage Size') }}</th>

                    <th data-column-id="storage_class" data-type="string" data-sortable="true" data-visible="false">{{ lang._('Storage Class') }}</th>
                    <th data-column-id="storage_etag" data-type="string" data-sortable="true" data-visible="false">{{ lang._('Storage ETag') }}</th>
                </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
            
        </div>
    </div>
    <div class="row">
        <div class="col-md-12">
            &nbsp;
        </div>
    </div>
</div>
