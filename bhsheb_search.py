from flask import render_template, request, url_for
from tf.fabric import Fabric
from kimsbible.bhsheb import api
from kimsbible import app

api.makeAvailableIn(globals())

@app.route('/bhsheb/search/', methods=['GET', 'POST'])
def bible_search():
    if request.method == 'POST':
        query = request.form['query']
        query = query.replace('שׁ', 'שׁ').replace('שׂ', 'שׂ')
        query = query.replace('ם','מ').replace('ך','כ').replace('ן','נ').replace('ף','פ').replace('ץ','צ')
        query = query.replace('ש1', 'שׁ').replace('ש2', 'שׂ')
        S.search(query)
        result = "<table class='table' id='paginated'><tbody>"
        i = 0

        fetch_data = list(S.fetch(limit=500))
        fetch_data.sort(key=lambda x: x[-1])

        for t in fetch_data:
            i = int(1)
            i = i + 1

            section = T.sectionFromNode(t[-1], lang='ko')
            v = T.nodeFromSection((section[0], section[1], section[2]), lang='ko')
            verse = ''

            wordsNode = L.d(v, otype='word')
            for w in wordsNode:
                clauseNode = L.u(w, otype='clause')
                phraseNode = L.u(w, otype='phrase')
                firstClauseWordNode = L.d(clauseNode[0], otype='word')[0]
                firstPhraseWordNode = L.d(phraseNode[0], otype='word')[0]
                lastClauseWordNode = L.d(clauseNode[0], otype='word')[-1]
                lastPhraseWordNode = L.d(phraseNode[0], otype='word')[-1]

                if w == firstClauseWordNode:
                    verse += '<span class=clauseNode_'+str(clauseNode[0])+'>'

                if w == firstPhraseWordNode:
                    verse += '<span class=phraseNode_'+str(phraseNode[0])+'>'

                verse += '<span class=wordNode_'+str(w)+'>'
                verse += F.g_word_utf8.v(w)
                verse += '</a></span>'

                if F.trailer_utf8.v(w):
                    verse += '<span class=trailerNode>'
                    verse += F.trailer_utf8.v(w)
                    verse += '</span>'

                if w == lastClauseWordNode: verse += '</span>'
                if w == lastPhraseWordNode: verse += '</span>'

            for each_node in t:
                node_type = F.otype.v(each_node)
                if(node_type == 'book' or node_type == 'chapter' or node_type == 'verse'): continue
                elif(node_type == 'clause'):
                    verse = verse.replace('clauseNode_'+str(each_node), 'clause')
                elif (node_type == 'phrase'):
                    verse = verse.replace('phraseNode_'+str(each_node), 'phrase')
                elif(node_type == 'word'):
                    verse = verse.replace('wordNode_'+str(each_node), 'word')
            result += '<tr><td width=180px><span verse_node=' + str(v) + '>'
            result += section[0] + " " + str(section[1]) + ":" + str(section[2]) + "</span>"
            result += '<p><button type="button" class="btn btn-secondary btn-sm bhsheb_verse_analysis" verse_node='+str(v)+'>절분석</button></p></td>'
            result += "<td class=result_verse>" + verse + "</td></tr>"

        result += "</tbody></table>"
        if i == 0:
            return False
        else:
            return result
    else:
        return render_template('bhsheb_search.html')
