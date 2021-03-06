$(function () {
    $("#query_post").submit(function () {
        $("#load_image").show();
        $("#query_submit").hide();

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

                $("#search_result_ok").html('검색결과: 총' + num +'개 결과값 <span class=clause style="padding:2px; font-size:15px">구절(clause)</span> <span class=phrase style="padding:2px; font-size:15px">구(phrase)</span> <span class=word style="font-size:15px">단어(word)</span><br>' + data);
                $("#query_input_ok").html('입력한 쿼리:<button type="button" class="btn btn-secondary btn-sm" id="copy_query">입력창에 복사</button><div id=used_query>' + input + '</div>');
                $("#query_post").find('textarea').val('');

                $.ajax({
                    url: "/static/js/table_pagination.js",
                    dataType: "script"
                });
                $.ajax({
                    url: "/static/js/copy_query.js",
                    dataType: "script"
                });
                $.ajax({
                    url: "/static/js/modal_word_api.js",
                    dataType: "script"
                });

                $("#load_image").hide();
                $("#query_submit").show();
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

                $("#query_input_ok").html('입력한 쿼리:<button type="button" class="btn btn-secondary btn-sm" id="copy_query">입력창에 복사</button><div id=used_query>' + input + '</div>');
                $("#search_result_ok").html('검색 결과가 없습니다. 검색 결과가 너무 많아도 결과값이 나오지 않습니다. 이 경우 검색 범위를 한정하는 것이 좋습니다.(<a href="/search_tutorial/" target=_blank>튜토리얼 참조</a>)');
                $("#query_post").find('textarea').val('');

                $.ajax({
                    url: "/static/js/copy_query.js",
                    dataType: "script"
                });

                $("#load_image").hide();
                $("#query_submit").show();
            });
        return false;
    });
});


$(function () {
  $.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);

    if(!results) {
      return '';
    }
    else {
      return results[1] || 0;
    }
  }

  var cons = $.urlParam('cons');
  var tense = $.urlParam('tense');
  var stem = $.urlParam('stem');
  var ps = $.urlParam('ps');
  var gn = $.urlParam('gn');
  var nu = $.urlParam('nu');
  var prs_ps = $.urlParam('prs_ps');
  var prs_gn = $.urlParam('prs_gn');
  var prs_nu = $.urlParam('prs_nu');
  // 동사 형태 출력이 아닌 용례 분석을 클릭해서 들어올 경우
  var sp = $.urlParam('sp');

  // 동사 형태 출력 페이지에서 url을 가지고 올 경우
  // if(cons || tense || stem || ps || gn || nu || prs_ps || prs_gn || prs_nu) {
  if(!sp && tense) {
    var que = "word lex_utf8=" + cons + " sp=verb vt=" + tense + " vs=" + stem;
    que += " ps=" + ps;
    que += " gn=" + gn;
    que += " nu=" + nu;
    que += " prs_ps=" + prs_ps;
    que += " prs_gn=" + prs_gn;
    que += " prs_nu=" + prs_nu;

    $('#query_text').val(decodeURIComponent(que));
  }

  else if(sp) {
    var que = "word lex_utf8=" + cons + " sp=" + sp;
    $('#query_text').val(decodeURIComponent(que));
  }

});
