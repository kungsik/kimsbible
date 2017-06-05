//k: json 상위값, s: 새로운 셀렉터 이름, t: 셀렉터를 입력시킬 타켓, c: 고유값(카테고리)
var loadJsonToSelector = function (k, s, c, t) {
    $.getJSON('/static/json/search_tree.json', function (data) {
        var new_selector = "<select name=" + s + " id=" + s +" class='form-control'>";
        $.each(data[k], function (key, value) {
            if(key == "title") {
              key = '';
              var option_value = "";
            }
            else {
              option_value = " book=";
            }
            new_selector += "<option value='" + option_value  + key + "' category=" + c + ">" + value +"</option>";
        });
        new_selector += "</select>";
        $(t).html(new_selector);
    });
};

//k: json 상위값, s: 새로운 셀렉터 이름, t: 셀렉터를 입력시킬 타켓, c: 고유값(카테고리)
var loadJsonToSelector2 = function (k, s, c, t) {
    $.getJSON('/static/json/search_tree.json', function (data) {
        var new_selector = "<select name=" + s + " id=" + s +" class='form-control'>";
        i = 0;
        $.each(data[k], function (key, value) {
            if(i==0){
                new_selector += "<option value='' category=" + c + ">" + value +"</option>";
            }
            else{
                if($.isArray(value)){
                    v = value[0]["title"];
                }
                else{
                    v = value;
                }
                new_selector += "<option value=" + key + " category=" + c + ">" + v +"</option>";
            }
            i++;
        });
        new_selector += "</select>";
        $(t).html(new_selector);
    });
};


//k1: json 최상위값(id값), k2: json 차상위값, s: 새로운 셀렉터 이름, t: 셀렉터를 입력시킬 타켓
var loadJsonToSelector3 = function (k1, k2, s, t) {
    $.getJSON('/static/json/search_tree.json', function (data) {
        var new_selector = "<select name=" + s + " id=" + s +" class='form-control'>";
        $.each(data[k1][k2][0], function (key, value) {
            if(key == "title") { key = ''; }
            new_selector += "<option value='=" + key + "'>" + value +"</option>";
        });
        new_selector += "</select>";
        $(t).html(new_selector);
    });
};


$('#search_helper').on('change', function () {
    $("#search_selector").empty();
    $("#search_selector2").empty();
    var init_selector = $("#search_helper option:selected").val();
    if(init_selector == "book"){
        loadJsonToSelector(init_selector, 'search_selector', 'book', '#search_selector');
    }
    if(init_selector == "clause"){
        loadJsonToSelector2(init_selector, 'search_selector', 'clause', '#search_selector');
    }
    if(init_selector == "phrase"){
        loadJsonToSelector2(init_selector, 'search_selector', 'phrase', '#search_selector');
    }
    if(init_selector == "word"){
        loadJsonToSelector2(init_selector, 'search_selector', 'word', '#search_selector');
    }
    if(init_selector == "chapter" || init_selector == "verse"){
        var new_input = "<input type='text' name='new_input' id='new_input' class='form-control' placeholder='" + init_selector + "입력'>"
        $("#search_selector").html(new_input);
    }
});


$('#search_selector').on('change', function () {
    $("#search_selector2").empty();
    var sec_selector_c = $('#search_selector option:selected').attr("category");
    var sec_selector = $("#search_selector option:selected").val();
    loadJsonToSelector3(sec_selector_c, sec_selector, 'new_selector', '#search_selector2');
});


$('#add_search').on('click', function () {
    var init_selector = $("#search_helper option:selected").val();
    var sec_selector = $("#search_selector option:selected").val();
    var new_selector = $("#new_selector option:selected").val();

    if(init_selector == 'book') {
        new_selector = "";
        if(!$("#search_selector option:selected").val()){
          sec_selector = "";
        }
    }

    if(init_selector == 'chapter' || init_selector == 'verse') {
        new_selector = "";
        if($('#new_input').val()){
          sec_selector = init_selector + '=' + $('#new_input').val();
        }
        else {
          sec_selector = "";
        }
    }

    if(init_selector == 'sentence') {
        sec_selector = "";
        new_selector = "";
    }

    if(init_selector == 'clause' || init_selector == 'phrase' || init_selector == 'word') {
        if(!$("#search_selector option:selected").val()){
          sec_selector = "";
          new_selector = "";
        }
        if(!$("#new_selector option:selected").val()){
          new_selector = "";
        }
    }

    if($('#query_text').val() && $('#check').is(":checked")){
        var newLine = " \n";
    }

    else if($('#query_text').val() && !$('#check').is(":checked")){
        init_selector = "";
        var newLine = "";
    }

    else {
        var newLine = "";
    }

    var txt = newLine + init_selector + ' ' + sec_selector + new_selector + ' ';
    $("#query_text").val($("#query_text").val() + txt);
});
