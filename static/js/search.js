$(function () {
    $("#query_post").submit(function () {
        var query_send = $.post('./', $('#query_post').serialize())
            .success(function () {
                var data = query_send.responseText;
                var input = $("#query_post").find("[id=query_text]").val();
                input = input.replace("book ","book&#32;");
                input = input.replace("chapter ","chapter&#32;");
                input = input.replace("verse ","verse&#32;");
                input = input.replace("sentence ","sentence&#32;");
                input = input.replace("verse ","verse&#32;");
                input = input.replace("clause ","clause&#32;");
                input = input.replace("phrase ","phrase&#32;");
                input = input.replace("word ","word&#32;");
                input = input.replace(/ /g, "&nbsp");
                input = input.replace(/\t/g, "&emsp;");
                input = input.replace("ש1", "שׁ");
                input = input.replace("ש2", "שׂ");
                input = input.replace("<", "&lt;");
                input = input.replace(">", "&gt;");
                input = input.replace(/\n/g, "<br>\n");

                $("#query_input").attr("id", "query_input_ok");
                $("#search_result").attr("id", "search_result_ok");

                var num = data.match(/<tr>/g).length;

                $("#search_result_ok").html('검색결과: 총' + num +'개 결과값<br>' + data);
                $("#query_input_ok").html('입력한 쿼리:<button type="button" class="btn btn-default btn btn-sm" id="copy_query">입력창에 복사</button><div id=used_query>' + input + '</div>');
                $("#query_post").find('textarea').val('');

                $.ajax({
                    url: "/static/js/table_pagination.js",
                    dataType: "script"
                });
                $.ajax({
                    url: "/static/js/copy_query.js",
                    dataType: "script"
                });
            })
            .error(function () {
                var input = $("#query_post").find("[id=query_text]").val();
                input = input.replace("book ","book&#32;");
                input = input.replace("chapter ","chapter&#32;");
                input = input.replace("verse ","verse&#32;");
                input = input.replace("sentence ","sentence&#32;");
                input = input.replace("verse ","verse&#32;");
                input = input.replace("clause ","clause&#32;");
                input = input.replace("phrase ","phrase&#32;");
                input = input.replace("word ","word&#32;");
                input = input.replace(/ /g, "&nbsp");
                input = input.replace(/\t/g, "&emsp;");
                input = input.replace("ש1", "שׁ");
                input = input.replace("ש2", "שׂ");
                input = input.replace("<", "&lt;");
                input = input.replace(">", "&gt;");
                input = input.replace(/\n/g, "<br>\n");



                $("#query_input").attr("id", "query_input_ok");
                $("#search_result").attr("id", "search_result_ok");

                $("#query_input_ok").html('입력한 쿼리:<button type="button" class="btn btn-default btn btn-sm" id="copy_query">입력창에 복사</button><div id=used_query>' + input + '</div>');
                $("#search_result_ok").html('검색 결과가 없습니다..');
                $("#query_post").find('textarea').val('');

                $.ajax({
                    url: "/static/js/copy_query.js",
                    dataType: "script"
                });
            });
        return false;
    });
});
