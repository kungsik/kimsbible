from flask import render_template, request, url_for
from tf.fabric import Fabric
from kimsbible.views import api
from kimsbible import app

api.makeAvailableIn(globals())

@app.route('/search_tutorial/')
def tutorial_page():
    return render_template('search_tutorial.html')

@app.route('/search_sample/')
def sample_page():
    return render_template('search_sample.html')


@app.route('/api/search/', methods=['GET', 'POST'])
def bible_search():
    if request.method == 'POST':
        query = request.form['query']
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

            clauseNode = L.d(v, otype='clause')
            for c in clauseNode:
                verse += '<span class=clauseNode_'+str(c)+'>'
                phraseNode = L.d(c, otype='phrase')
                for p in phraseNode:
                    verse += '<span class=phraseNode_'+str(p)+'>'
                    wordsNode = L.d(p, otype='word')
                    for w in wordsNode:
                        verse += '<span class=wordNode_'+str(w)+'>'
                        verse += F.g_word_utf8.v(w)
                        verse += '</a></span>'
                        if F.trailer_utf8.v(w):
                            verse += '<span class=trailerNode>'
                            verse += F.trailer_utf8.v(w)
                            verse += '</span>'
                    verse += '</span>'
                verse += '</span>'
            verse += '</span>'

            for each_node in t:
                node_type = F.otype.v(each_node)
                if(node_type == 'book' or node_type == 'chapter' or node_type == 'verse'): continue
                elif(node_type == 'clause'):
                    verse = verse.replace('clauseNode_'+str(each_node), 'clause')
                elif (node_type == 'phrase'):
                    verse = verse.replace('phraseNode_'+str(each_node), 'phrase')
                elif(node_type == 'word'):
                    verse = verse.replace('wordNode_'+str(each_node), 'word')
            result += "<tr><td width=180px><span class=verse_num verse_node=" + str(v) + ">" + section[0] + " " + str(section[1]) + ":" + str(section[2]) + "</span></td><td class=result_verse>" + verse + "</td></tr>"

        result += "</tbody></table>"
        if i == 0:
            return False
        else:
            return result
    else:
        return render_template('search.html')
