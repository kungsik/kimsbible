$(function () {
    $("#parsing_post").submit(function () {
        $("#load_image").show();
        $("#parsing_submit").hide();


        if($('#check1').is(':checked')){
            checkarr[0].value = 'Y'
        }
        if($('#check2').is(':checked')){
            checkarr[1].value = 'Y'
        }

        var parsing_send = $.post('./', $('#parsing_post').serialize())
            .success(function () {
                var data = parsing_send.responseText;

                $("#search_result").attr("id", "search_result_ok");
                $("#search_result_ok").html(data);

                $("#load_image").hide();
                $("#parsing_submit").show();
            })
            .error(function () {

                $("#search_result_ok").html('검색 결과가 없습니다..');

                $("#load_image").hide();
                $("#parsing_submit").show();
            });
        return false;
    });
});
