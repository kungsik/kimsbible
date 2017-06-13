 $(function () {
     $(document.body).on('click', '#syntax_enact', function () {
         $(this).html('구절/구문단위가리기');
         $(this).attr('id', 'syntax_disable');
         $('.clauseNode, .phraseNode').each(function () {
             $('.clauseNode').attr('class', 'clause text');
             $('.phraseNode').attr('class', 'phrase');
         });

         $(document.body).on('click', '#syntax_disable', function () {
             $(this).html('구절/구문단위표시');
             $(this).attr('id', 'syntax_enact');
             $('.clause, .phrase').each(function () {
                 $('.clause').attr('class', 'clauseNode');
                 $('.phrase').attr('class', 'phraseNode');
             });
         });
     });
 });