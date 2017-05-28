
$(function(){
    $(".word_elm").click(function(){
        var word_node = $(this).attr("word_node");
        $('div.modal').modal({remote : '/api/word/'+word_node});
    })
})
