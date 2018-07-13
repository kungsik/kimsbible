 $(function() {
   $(document.body).on('click', '#syntax_enact', function() {
     $(this).html('절(C)/구(P)단위가리기');
     $(this).attr('id', 'syntax_disable');
     $('.clauseNode, .phraseNode').each(function() {
       $('.clauseNode').attr('class', 'clause');
       $('.phraseNode').attr('class', 'phrase');
       $('.syntax.clause1.hidden').attr('class', 'syntax clause1');
       $('.syntax.phrase1.hidden').attr('class', 'syntax phrase1');
     });

     $(document.body).on('click', '#syntax_disable', function() {
       $(this).html('절(C)/구(P)단위표시');
       $(this).attr('id', 'syntax_enact');
       $('.clause, .phrase').each(function() {
         $('.clause').attr('class', 'clauseNode');
         $('.phrase').attr('class', 'phraseNode');
         $('.syntax.clause1').attr('class', 'syntax clause1 hidden');
         $('.syntax.phrase1').attr('class', 'syntax phrase1 hidden');
       });
     });
   });
 });


 $(function() {
   $(document.body).on('click', '#verse_block', function() {
     $(this).html('절(verse)구분해제');
     $(this).attr('id', 'verse_inline');
     $('.verseNode').each(function() {
       $('.verseNode').css('display', 'block');
       $('.verseNode').css('text-indent', '-1.2em');
     });

     $(document.body).on('click', '#verse_inline', function() {
       $(this).html('절(verse)구분');
       $(this).attr('id', 'verse_block');
       $('.verseNode').each(function() {
        $('.verseNode').css('text-indent', '0em');
        $('.verseNode').css('display', 'inline');
       });
     });
   });
 });

 $(function() {
   $(document.body).on('click', '#geoinfo', function() {
     $(this).html('지도숨기기');
     $(this).attr('id', 'geoinfo_hide');
     $('#map-canvas').toggle({
       complete: function() {
         initialize();
       },
       duration: 'slow'
     });
     $('#map-comment').css('display', 'block');

     $(document.body).on('click', '#geoinfo_hide', function() {
       $(this).html('지도표시');
       $(this).attr('id', 'geoinfo');
       $('#map-canvas').css('display', 'none');
       $('#map-comment').css('display', 'none');
     });
   });
 });
