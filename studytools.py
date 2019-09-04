from tf.fabric import Fabric
from flask import render_template, request, url_for
from kimsbible import app
from kimsbible.bhsheb import api
from kimsbible.bhsheb import get_strong, get_kor_hgloss
from collections import OrderedDict
from kimsbible.lib import lib as kb
from kimsbible import bhsheb_stat as stat
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
import random

api.makeAvailableIn(globals())

@app.route('/studytools/reading/', methods=['GET', 'POST'])
def studytools():
    if request.method == 'POST':      
        rangeCode = request.form['rangeCode']
        check1 = request.form['check1']
        check2 = request.form['check2']
        check3 = request.form['check3']

        sections = rangeCode.split(";")

        result = '<div class="reading">'
        result += '<h3>본문읽기(구약 히브리어)</h3><br>'

        if not check1:
            parsing = '<h4>단어 문법 분석</h4>'
            parsing += '<br><div class="parsing">'


        vocalist = {}

        for section in sections:
            nodeList = stat.codetorange(section)
            sectionTitle = stat.codetostr(section, stat.bookListKor)
        
            if nodeList == False: return False
            
            result += '<h4>' + sectionTitle + '</h4>'
            result += '<br>'
            result += '<div class="section">'
            
            for node in nodeList:
                section = T.sectionFromNode(node)
                wordsNode = L.d(node, otype='word')
                result += '<span class=chpvrs>' + str(section[2]) + '</span> <span class="verse">' + T.text(wordsNode) + '</span>'

                if not check1:
                    parsing += str(section[1]) + ":" + str(section[2]) + "<br>"

                for w in wordsNode:
                    strong = get_strong(w)
                    gloss = get_kor_hgloss(strong, w)

                    if not check2:
                        root = F.voc_utf8.v(L.u(w, otype='lex')[0])

                        if not root in vocalist:
                            vocalist[root] = gloss

                    if not check1:                  
                        parsing += '<span class="parsing_heb">'
                        parsing += "[" + F.g_word_utf8.v(w) + "] "
                        parsing += "</span>"

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

                        parsing += "(" + gloss + ")<br>"
            
            result += '</div><br><br>'
        
        if not check1:
            parsing += '</div><br><br>'
            result += parsing

        if not check2:
            result += '<h4>단어 리스트</h4>'
            result += '<br>'
            result += '<div class="wordlist">'

            sorted_vocalist = sorted(vocalist.items())
            for voca in sorted_vocalist:
                result += '<span class="parsing_heb">' + voca[0] + '</span> <span class="parsing">' + voca[1] + '</span><br>'
            
            result += '</div>'
        
        result += '</div>'

        if check3:
            # font_config = FontConfiguration()
            # randnum = random.random()
            # html = HTML(string=result)

            # css_string = '''
            #     @import url('https://fonts.googleapis.com/css?family=David+Libre&display=swap');
            #     .reading {
            #         font-family: 'David Libre', serif;
            #     }
            #     .section {
            #         font-family: 'Nanum Gothic', serif;
            #         font-size: 25px;
            #         direction:rtl; 
            #         text-align:right; 
            #     }
            # '''
                        
            # css = CSS(string=css_string, font_config=font_config)
            
            # html.write_pdf(
            #     'kimsbible/static/tmp/reading.pdf', 
            #     stylesheets=[css])
            
            # makelink = '<div>PDF링크가 생성되었습니다. 링크를 클릭해 주세요.<a href="http://127.0.0.1:5000/static/tmp/reading.pdf?v=' + str(randnum) + '" target="_blank">다운로드</a></div>'

            return render_template('studytools_reading_pdf.html', result=result)
        
        return result

    else:
        return render_template('studytools_reading.html')
