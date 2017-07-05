$(function(){
  var hebrew = ["א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט", "י", "כ", "ל", "מ", "נ", "ס", "ע", "פ", "צ", "ר", "ש", "ת"];
  var hebrewkey = "";

  for(var i=0; i<hebrew.length; i++) {
    hebrewkey += "<button class='btn btn-default btn-xs' letter="+ hebrew[i] + ">" + hebrew[i] + "</button>";
    if(i==10) {
      hebrewkey += "<br>";
    }
  }
  $("#hebrewkey").html(hebrewkey);
});

$(function(){
  $(".btn-xs").click(function(){
    var hebrewletter = $(this).attr("letter");
    $("#verb").val($("#verb").val() + hebrewletter)
  });
});
