from tf.fabric import Fabric
from flask import render_template, request, url_for
from kimsbible import app
from kimsbible.bhsheb import api
from kimsbible.bhsheb import get_strong, get_kor_hgloss
from collections import OrderedDict
from kimsbible.lib import lib as kb
from kimsbible import bhsheb_stat as stat

api.makeAvailableIn(globals())

@app.route('/studytools/reading/', methods=['GET', 'POST'])
def studytools():
    if request.method == 'POST':
        rangeCode = request.form['rangeCode']
        sections = rangeCode.split(";")

        result = '<h3>본문읽기(구약 히브리어)</h3>'
        vocalist = {}

        for section in sections:
            nodeList = stat.codetorange(section)
            sectionTitle = stat.codetostr(section, stat.bookListKor)
        
            if nodeList == False: return False
            
            result += '<h4>' + sectionTitle + '</h4>'
            result += '<br>'
            result += '<div class="section" style="direction:rtl; text-align:right; column-count: 2;">'
            
            for node in nodeList:
                section = T.sectionFromNode(node)
                wordsNode = L.d(node, otype='word')
                result += '<span class=chpvrs>' + str(section[2]) + '</span> <span class="verse">' + T.text(wordsNode) + '</span>'

                for w in wordsNode:
                    root = F.voc_utf8.v(L.u(w, otype='lex')[0])
                    strong = get_strong(w)
                    gloss = get_kor_hgloss(strong, w)

                    if not root in vocalist:
                        vocalist[root] = gloss
            
            result += '</div><br><br>'

        result += '<h3>단어 리스트</h3>'
        result += '<br>'
        result += '<div style="column-count: 3;">'
        sorted_vocalist = sorted(vocalist.items())
        for voca in sorted_vocalist:
            result += '<span>' + voca[0] + ' ' + voca[1] + '</span><br>'
        
        result += '</div>'
        return result

    else:
        return render_template('studytools_reading.html')
