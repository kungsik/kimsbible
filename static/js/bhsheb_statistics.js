$(function () {
    $("#stat_post").submit(function () {
        $("#load_image").show();
        $("#stat_submit").hide();

        var stat_send = $.post('./', $('#stat_post').serialize())
            .success(function () {
                var data = stat_send.responseText;

                $("#search_result").attr("id", "search_result_ok");
                $("#search_result_ok").html(data);

                $("#load_image").hide();
                $("#stat_submit").show();
            })
            .error(function () {

                $("#search_result_ok").html('검색 결과가 없습니다..');

                $("#load_image").hide();
                $("#stat_submit").show();
            });
        return false;
    });
});
