
$(function(){
    $(".word_elm").click(function(){
        var word_node = $(this).attr("word_node");
        $('div.modal').modal({remote : '/api/word/'+word_node});
    })
})

$(function(){
    $(".verse_num").click(function(){
        var verse_node = $(this).attr("verse_node");
        $('div.modal').modal({remote : '/api/verse/'+verse_node});
    })
})
