google.load('visualization', '1', {packages:['corechart', 'timeline'], 'language': 'pl'});
function parseInterval(value) {
    var result = new Date('1, 1, 1, ' + value);
    return result;
}

(function($) {
    $(document).ready(function(){
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
                $chartDiv = $('#chart_div');

            if($selectedUser) {
                $loading.show();
                $chartDiv.hide();

                $.getJSON('api/v1/get_avatar/' + $selectedUser, function(result){
                    $('#avatar').attr('src', result['avatar']);
                });

                $.getJSON('/api/v1/presence_start_end/' + $selectedUser, function(result) {
                    var finalResult = [],
                        options = {
                            hAxis: {title: 'Weekday'}
                        },
                        data = new google.visualization.DataTable(),
                        formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'}),
                        chart = new google.visualization.Timeline($chartDiv[0]);

                    $.each(result, function(day, intervals) {
                        finalResult.push([
                            day,
                            parseInterval(intervals['start']),
                            parseInterval(intervals['end'])
                        ])
                    });

                    // some dummy data, this should go from API
                    data.addColumn('string', 'Weekday');
                    data.addColumn({type: 'datetime', id: 'Start'});
                    data.addColumn({type: 'datetime', id: 'End'});
                    data.addRows(finalResult);

                    formatter.format(data, 1);
                    formatter.format(data, 2);

                    $chartDiv.show();
                    $loading.hide();
                    chart.draw(data, options);
                }).fail(function() {
                    alert('User not found!');
                });
            }
        });
    });
})(jQuery);
