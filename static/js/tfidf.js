$(function () {
    $("#tfidf").submit(function () {
        $("#load_image").show();
        $("#tfidf_submit").hide();

        var tfidf_send = $.post('./', $('#tfidf').serialize())
            .success(function () {
                var output = ''
                var data = $.parseJSON(tfidf_send.responseText)
                if(data == false){
                  output = "<div class='alert alert-danger' role='alert' style='font-size:20px; text-align:center'>입력값에 오류가 있습니다.</div>";
                }
                else {
                  output += "<div class='row'>"
                  output += "<div class='col-md-6'>"
                  $.each(data[0], function(key, value) {
                    output += key + " " + value + "<br>"
                  });
                  output += "</div>"

                  output += "<div class='col-md-6'>"
                  $.each(data[1], function(key2, value2) {
                    output += key2 + " " + value2 + "<br>"
                  });
                  output += "</div></div>"
                }

                $("#load_image").hide();
                $("#tfidf_submit").show();

                $("#tf_idf_result").html(output)
            })
            .error(function () {
                alert("오류");

                $("#load_image").hide();
                $("#tfidf_submit").show();
            });
        return false;
    });
});
