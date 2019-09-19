$(function(){
  var hebrew = ["א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט", "י", "כ", "ל", "מ", "נ", "ס", "ע", "פ", "צ" ,"ק", "ר", "ש", "ת"];
  var hebrewkey = "";

  for(var i=0; i<hebrew.length; i++) {
    hebrewkey += "<button class='btn btn-outline-info btn-sm' style='margin-bottom:3px; margin-right:2px; width: 27.3px' letter=" + hebrew[i] + ">" + hebrew[i] + "</button>";
    if(i==10) {
      hebrewkey += "<br>";
    }
  }
  $("#hebrewkey").html(hebrewkey);
});

$(function(){
  $(".btn-sm").click(function(){
    var hebrewletter = $(this).attr("letter");
    $("#verb").val($("#verb").val() + hebrewletter)
  });
});
