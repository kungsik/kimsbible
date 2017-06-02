
$(function(){
    var path = location.pathname.split('/');
    var book = path[2];
    var chapter = path[3];

    //bible_selector id를 찾아 select 값 부여.
    //$('#bible_selector[value='...']').attr("selected", "selected"); 과 동일한 효과 그런데 이 방식은 변수 인식이 어려움.
    $('#bible_selector').val('/text/' + book);

    var chp = $("#bible_selector option:selected").attr("chp");
    for(var i=1; i <= chp; i++){
        if(i == chapter) {
            $("#chp_selector").append("<option value='/text/" + chapter + "/"+i+"' selected>"+i+"</option>");
        }
        else {
            $("#chp_selector").append("<option value='/text/" + book + "/"+i+"'>"+i+"</option>");
        }
    }

});