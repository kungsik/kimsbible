$(function(){
    $(".verse_num").click(function(){
        var verse_node = $(this).attr("verse_node");
        $('div.modal').modal({remote : '/api/verse/'+verse_node});
    })
})

$(function(){
    $('*[data-poload]').click(function() {
        var e = $(this);
        $.get(e.data('poload'), function(d) {
            e.popover({
                content: d,
                title: '단어분석',
                html: true,
                constraints: [
                    {
                        to: '.container', pin: true
                    }
                ]
            }).popover('show');
        })
    })
    $('.popover-dismiss').popover({
        trigger: 'focus'
    })
})