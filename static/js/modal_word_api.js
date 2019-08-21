// $(document).ready(function(){
//     $(".verse_num").click(function(){
//         var verse_node = $(this).attr("verse_node");
//         $('div.modal').modal({remote : '/api/verse/'+verse_node});
//     })
// });

$(document).ready(function(){
    $(".bhsheb_verse_analysis").click(function(){
        var verse_node = $(this).attr("verse_node");
        var url = '/bhsheb/verse/'+verse_node;
        $('.modal-container').load(url, function(result){
            $('#verse_api').modal({show:true});
        });
    });
});

$(document).ready(function(){
    $(".verse_note").click(function(){
        var vcode = $(this).attr("vcode");
        var url = '/commentary/list/';
        $('.modal-container').load(url, function(result){
            $('#commentary').modal({show:true});
        });
    });
});

$(document).ready(function(){
    $(".sblgnt_verse_analysis").click(function(){
        var verse_node = $(this).attr("verse_node");
        var url = '/sblgnt/verse/'+verse_node;
        $('.modal-container').load(url, function(result){
            $('#verse_api').modal({show:true});
        });
    });
});

$(document).ready(function(){
    $('*[data-poload]').click(function() {
        var e = $(this);
        $.get(e.data('poload'), function(d) {
            e.popover({
                content: d, //+ e.position().left,
                title: '<div class=poptitle>단어분석 <button class=close> X</button></div>',
                html: true,
                constraints: [
                    {
                        to: '.container', pin: true
                    }
                ],
                placement: function(){
                  var position = e.position();
                  if (position.left < 100) {
                    return 'right';
                  }
                  if (position.left > 100 && position.left < 200 ) {
                    return 'top';
                  }
                  if (position.left > 200) {
                    return "left";
                  }
                }
            }).popover('show');
			$('body')
			  .on('mousedown', '.word_api', function(e) {
			    e.preventDefault();
			});
        })
    });
    $('.close').click(function() {
        e.popover('hide');
    })
});


