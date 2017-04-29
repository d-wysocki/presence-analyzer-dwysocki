google.load('visualization', '1', {packages:['corechart', 'timeline'], 'language': 'pl'});
function toDateTime(secs) {
    var result = new Date(0, 0, 1);
    result.setSeconds(secs);
    return result;
}

(function($) {
    $(document).ready(function(){
        var $loading = $('#loading'),
            $chartDiv = $("#chart_div");

        $loading.hide();
        $chartDiv.show();

        $.getJSON('/api/v1/overtime/', function(result) {
            var finalResult = [],
                chart = new google.visualization.Timeline($chartDiv[0]),
                dataTable = new google.visualization.DataTable(),
                options = {hAxis: { format: 'd, H:mm:ss' }};

            $.each(result, function(index, intervals) {
                finalResult.push([
                    (index + 1).toString(),
                    intervals[1]['name'].toString(),
                    new Date(0, 0, 1, 0, 0, 0),
                    toDateTime(intervals[1]['overtime']),
                ])
            });

            dataTable.addColumn({ type: 'string', id: 'Position' });
            dataTable.addColumn({ type: 'string', id: 'Name' });
            dataTable.addColumn({ type: 'date', id: 'Start' });
            dataTable.addColumn({ type: 'date', id: 'End' });
            dataTable.addRows(finalResult);

            chart.draw(dataTable, options);
        }).fail(function() {
            alert('User not found!');
        });
    });
})(jQuery);
