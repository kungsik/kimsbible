$(function () {
    $("#query_post").submit(function () {
        var query_send = $.post('./', $('#query_post').serialize())
            .success(function () {
                var data = query_send.responseText;
                var input = $("#query_post").find("[id=query_text]").val();
                input = input.replace(/\n/g, "<br>\n");
                input = input.replace(/ /g, "&nbsp");
                input = input.replace(/\t/g, "&emsp;");

                $("#query_input").attr("id", "query_input_ok");
                $("#search_result").attr("id", "search_result_ok");

                var num = data.match(/<tr>/g).length;

                $("#search_result_ok").html('검색결과: 총' + num +'개 결과값<br>' + data);
                $("#query_input_ok").html('입력한 쿼리:<br>' + input);
                $("#query_post").find('textarea').val('');

                $.ajax({
                    url: "/static/js/table_pagination.js",
                    dataType: "script"
                });
            })
            .error(function () {
                var input = $("#query_post").find("[id=query_text]").val();
                input = input.replace(/\n/g, "<br>\n");
                input = input.replace(/ /g, "&nbsp");
                input = input.replace(/\t/g, "&emsp;");

                $("#query_input").attr("id", "query_input_ok");
                $("#search_result").attr("id", "search_result_ok");

                $("#query_input_ok").html('입력한 쿼리:<br>' + input);
                $("#search_result_ok").html('검색 결과가 없습니다..');
                $("#query_post").find('textarea').val('');
            });
        return false;
    });
});