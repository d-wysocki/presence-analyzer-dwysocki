google.load('visualization', '1', {packages:['corechart'], 'language': 'en'});
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
            $('#user_id').change(function(){
                var $selectedUser = $('#user_id').val(),
                    $chartDiv = $('#chart_div');

                $.getJSON('api/v1/get_avatar/' + $selectedUser, function(result) {

                    $('#avatar').attr('src', result['avatar']);
                });

                if($selectedUser) {
                    $loading.show();
                    $chartDiv.hide();

                    $.getJSON('/api/v1/presence_weekday/' + $selectedUser, function(result) {
                        if(result[404]) {
                            $loading.hide();
                            $('#message').replaceWith( '<h3>' + result[404] + '</h3>' );
                            return false;
                        }
                        var data = google.visualization.arrayToDataTable(result),
                            options = {},
                            chart = new google.visualization.PieChart($chartDiv[0]);

                        $chartDiv.show();
                        $loading.hide();
                        chart.draw(data, options);
                    })
                }
            });
        });
    })(jQuery);
