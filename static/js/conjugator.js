$(function() {
  $("#conjugator").submit(function() {
    $("#load_image").show();
    $("#conj_submit").hide();

    var conj_send = $.post('./', $('#conjugator').serialize())
      .success(function() {
        var data = $.parseJSON(conj_send.responseText)
        if (data == false) {
          var output = "<div class='alert alert-danger' role='alert' style='font-size:20px; text-align:center'>입력하신 단어가 동사인지 확인해 주세요.</div>";
        } else {
          var output = "<table class=table>"
          for (var i in data) {
            output += "<tr><td align=right width=30%>" + data[i].verb + "</td>";
            output += "<td>" + data[i].lang + " " + data[i].stem + " " + data[i].tense + " " + data[i].ps + " " + data[i].gn + " " + data[i].nu;
            if (data[i]['prs_ps']) {
              output += " + " + data[i]['prs_ps'] + " " + data[i]['prs_gn'] + " " + data[i]['prs_nu'];
            }
            output += "</td><td width=30%>" + data[i].query + "</td></tr>"
          }
          output += "</table>"
        }

        $("#load_image").hide();
        $("#conj_submit").show();

        $("#verballist").html(output)
      })
      .error(function() {
        alert("오류");

        $("#load_image").hide();
        $("#conj_submit").show();
      });
    return false;
  });
});

//get값으로 변수가 전달되었을 때 input에 그 값을 넣어 줌.
$(function() {
  $.urlParam = function(name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);

    if (!results) {
      return '';
    } else {
      return results[1] || 0;
    }
  }

  var cons = $.urlParam('cons');

  if (cons) {
    $('#verb').val(decodeURIComponent(cons));
  }

});
