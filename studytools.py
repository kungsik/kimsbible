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
        check1 = request.form['check1']
        check2 = request.form['check2']

        sections = rangeCode.split(";")

        result = '<h3>본문읽기(구약 히브리어)</h3><br>'

        if not check1:
            parsing = '<h3>단어 문법 분석</h3>'
            parsing += '<br><div style="column-count: 2;">'

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

                if not check1:
                    parsing += str(section[1]) + ":" + str(section[2]) + "<br>"

                for w in wordsNode:

                    if not check2:
                        root = F.voc_utf8.v(L.u(w, otype='lex')[0])
                        strong = get_strong(w)
                        gloss = get_kor_hgloss(strong, w)

                        if not root in vocalist:
                            vocalist[root] = gloss

                    if not check1:                  
                        parsing += '<span class="parsing">'
                        parsing += "[" + F.g_word_utf8.v(w) + "] "

                        pdp = kb.eng_to_kor(F.pdp.v(w), 'full')
                        parsing += pdp + " "
                    
                        if pdp == '동사':
                            parsing += "(" + F.voc_utf8.v(L.u(w, otype='lex')[0]) + ") "
                            parsing += kb.eng_to_kor(F.vs.v(w), 'full') + "." + kb.eng_to_kor(F.vt.v(w), 'full') + "." + kb.eng_to_kor(F.ps.v(w), 'full') + "." + kb.eng_to_kor(F.gn.v(w), 'full') + "." + kb.eng_to_kor(F.nu.v(w), 'full') + " "
                            if F.prs_ps.v(w) != 'unknown':
                                parsing += "접미."
                                parsing += kb.eng_to_kor(F.prs_ps.v(w), 'full') + "." + kb.eng_to_kor(F.prs_gn.v(w), 'full') + "." + kb.eng_to_kor(F.prs_nu.v(w), 'full') + " "
                        
                        if pdp == '명사':
                            parsing += "(" + F.voc_utf8.v(L.u(w, otype='lex')[0]) + ") "
                            parsing += kb.eng_to_kor(F.gn.v(w), 'full') + "." + kb.eng_to_kor(F.nu.v(w), 'full') + " "
                        
                        if F.g_prs_utf8.v(w) != "":
                            parsing += "접미." + kb.eng_to_kor(F.prs_ps.v(w), 'full') + "." + kb.eng_to_kor(F.prs_gn.v(w), 'full') + "." + kb.eng_to_kor(F.prs_nu.v(w), 'full') + " "

                        parsing += "(" + gloss + ")</span><br>"
            
            result += '</div><br><br>'
        
        if not check1:
            parsing += '</div><br><br>'
            result += parsing

        if not check2:
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
