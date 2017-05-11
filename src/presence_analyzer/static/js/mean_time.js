google.load("visualization", "1", {packages:["corechart"], 'language': 'pl'});
function parseInterval(value) {
    var result = new Date(0, 0, 0);
    result.setMilliseconds(value * 1000);
    return result;
}

(function($) {
    $(document).ready(function() {
        var $loading = $('#loading');

        $.getJSON('/api/v1/users_xml', function(result) {
            var $dropdown = $('#user_id');
            $.each(result, function(item) {
                $dropdown.append(
                    $('<option />', {
                        'val': this.user_id,
                        'text': this.name
                    })
                );
            });
            $dropdown.show();
            $loading.hide();
        });

        $('#user_id').change(function() {
            var $selectedUser = $('#user_id').val(),
                $chartDiv = $("#chart_div"),
                $message = $("#message");
            if($selectedUser === '') {
                $("#avatar").hide();
                $chartDiv.hide();
                $message.empty();
            } else {
                $message.empty();
                $loading.show();
                $chartDiv.hide();

                $.getJSON('api/v1/get_avatar/' + $selectedUser, function(result) {
                    $('#avatar').attr('src', result['avatar']);
                });

                $.getJSON('/api/v1/mean_time_weekday/' + $selectedUser, function(result) {
                    if(result['status'] === 404) {
                        $loading.hide();
                        $message.text(result['message']);
                        return;
                    }
                    var data = new google.visualization.DataTable(),
                        options = {
                            hAxis: {title: 'Weekday'}
                        },
                        formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'}),
                        chart = new google.visualization.ColumnChart($chartDiv[0]);

                    $.each(result, function(index, value) {
                        value[1] = parseInterval(value[1]);
                    });

                    data.addColumn('string', 'Weekday');
                    data.addColumn('datetime', 'Mean time (h:m:s)');
                    data.addRows(result);

                    formatter.format(data, 1);
                    $chartDiv.show();
                    $loading.hide();
                    chart.draw(data, options);
                })
            }
        });
    });
})(jQuery);
