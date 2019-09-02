$(function() {
  var hebrew = ["א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט", "י", "כ", "ל", "מ", "נ", "ס", "ע", "פ", "צ", "ק", "ר", "ש", "ת"];
  var hebrewkey = "";

  for (var i = 0; i < hebrew.length; i++) {
    hebrewkey += "<button class='btn btn-default btn-xs' letter=" + hebrew[i] + ">" + hebrew[i] + "</button>";
    if (i == 10) {
      hebrewkey += "<br>";
    }
  }
  $("#hebrewkey").html(hebrewkey);
});

$(function() {
  $(".btn-xs").click(function() {
    var txtArea = $("#query_text").get(0);
    var hebrewletter = $(this).attr("letter");
    var txtValue = $("#query_text").val(); // 텍스트 영역 값 가져오기
    var cursorPos = txtArea.selectionStart; //커서 위치
    var beforeTxt = txtValue.substring(0, cursorPos);  // 기존텍스트 ~ 커서시작점 까지의 문자
    var afterTxt = txtValue.substring(txtArea.selectionEnd, txtValue.length);   // 커서끝지점 ~ 기존텍스트 까지의 문자
 
    $("#query_text").val(beforeTxt + hebrewletter + afterTxt);

    cursorPos = cursorPos + hebrewletter.length;
    txtArea.selectionStart = cursorPos; // 커서 시작점을 추가 삽입된 텍스트 이후로 지정
    txtArea.selectionEnd = cursorPos; // 커서 끝지점을 추가 삽입된 텍스트 이후로 지정
    txtArea.focus();
  });
});
