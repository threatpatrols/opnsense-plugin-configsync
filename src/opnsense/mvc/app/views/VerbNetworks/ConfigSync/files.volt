
<script>
    
    function sortTable() {
        // Credit: https://www.w3schools.com/howto/howto_js_sort_table.asp
        var table, rows, switching, i, x, y, shouldSwitch;
        table = document.getElementById("filelist");
        switching = true;
        while (switching) {
            switching = false;
            rows = table.getElementsByTagName("tr");
            for (i = 1; i < (rows.length - 1); i++) {
                shouldSwitch = false;
                x = rows[i].getElementsByTagName("td")[0];
                y = rows[i + 1].getElementsByTagName("td")[0];
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            }
            if (shouldSwitch) {
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
            }
        }
    }    

    /**
     * updateFileTable
     */
    function updateFileTable() {
        
        $("#responseMsg").removeClass("hidden").removeClass("alert-danger").addClass('alert-info').html("Retreiving list of configuration files at the storage-provider...");
        
        ajaxGet('/api/configsync/files/get', {}, function (data, status) {
            if(status == 'parsererror' || data['status'] != 'success') {
                $("#responseMsg").addClass("alert-danger").removeClass('alert-info').html("Unable to retrieve list of configuration files at the storage-provider");
                $('#filelist > tbody').empty();
            }
            else {
                $("#responseMsg").addClass('hidden').html("");
                $('#filelist > tbody').empty();
                $.each(data['data'], function(filename, filedata) {
                    created = filedata['MetaData']['Created'] === undefined ? 'unknown' : filedata['MetaData']['Created'];
                    $('#filelist > tbody').append(
                        '<tr>' +
                        '<td>' + created + '</td>' +
                        '<td>' + filedata['LastModified'] + '</td>' +
                        '<td>' + filedata['Key'] + '</td>' +
                        '</tr>'
                    );
                });
                sortTable();
            }
        });
    }

    $( document ).ready(function() {
        updateFileTable(true);
    });
    
</script>


<div class="container-fluid">
    <div class="row">
        <div class="alert alert-info hidden" role="alert" id="responseMsg"></div>
    </div>
    <div class="row">
        <div class="col-md-12" id="content">
            
            <table class="table table-striped table-condensed table-responsive" id="filelist">
              <thead>
                <tr>
                  <th>{{ lang._('Created') }}</th>
                  <th>{{ lang._('Synced') }}</th>
                  <th>{{ lang._('Storage Provider Path') }}</th>
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
