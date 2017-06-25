import re
from collections import OrderedDict

from flask import render_template, request, url_for
from tf.fabric import Fabric

from kimsbible import app
from kimsbible.lib import lib as kb

### Load up TF ###
ETCBC = 'hebrew/etcbc4c'
TF = Fabric(locations='text-fabric-data', modules=ETCBC)
api = TF.load('''
    book chapter verse
    nu gn ps vt vs st
    otype typ function
    det pdp
    g_word_utf8 trailer_utf8
    lex_utf8 lex voc_utf8
    g_prs_utf8 g_uvf_utf8
    prs_gn prs_nu prs_ps g_cons_utf8
    gloss g_lex_utf8 phono
''')
api.makeAvailableIn(globals())

def word_function(node):
    w_f = OrderedDict()
    w_f["원형"] = F.voc_utf8.v(L.u(node, otype='lex')[0])
    #w_f["어근"] = F.lex_utf8.v(node).replace('=', '').replace('/', '').replace('[', '')
    w_f["음역"] = F.phono.v(node)
    w_f["품사"] = F.pdp.v(node)  # part of speech (verb, subs ..)
    w_f["시제"] = F.vt.v(node)  # vt = verbal tense
    w_f["동사형"] = F.vs.v(node)  # vs = verbal stem
    w_f["인칭"] = F.ps.v(node)  # person (p1, p2, p3)
    w_f["성"] = F.gn.v(node)  # gender
    w_f["수"] = F.nu.v(node)  # number (sg, pl, du)
    w_f["어형"] = F.st.v(node)  # construct/absolute/emphatic
    # w_f["접미어유무"] = "Yes" if F.g_prs_utf8.v(node) != "" else "No"
    w_f["인칭접미어"] = F.g_prs_utf8.v(node)  # pronominal suffix in Heb
    w_f["부가접미어"] = F.g_uvf_utf8.v(node)  # univalent final in Heb
    w_f["인칭(접미)"] = F.prs_ps.v(node)  # pronominal suffix person
    w_f["성(접미)"] = F.prs_gn.v(node)  # pronominal suffix gender
    w_f["수(접미)"] = F.prs_nu.v(node)  # pronominal suffix number
    w_f["의미"] = F.gloss.v(L.u(node, otype='lex')[0])
    return w_f

#node: 범위값; synType: clause, phrase, word; feat: 문법요소; num: 상위 몇개까지 줄력할지.
def featureStat(node, synType, feat, num):
    statType = {}
    total_num = 0
    for verseNode in node:
        statNode = L.d(verseNode, otype = synType)
        for n in statNode:
            total_num = total_num + 1

            if total_num > 40000: return False

            if feat == 'lex_utf8': sType = F.lex_utf8.v(L.u(n, otype='lex')[0])
            elif feat == 'pdp': sType = F.pdp.v(n)
            elif feat == 'psgnnu':
                sType = F.ps.v(n) + "-" + F.gn.v(n) + "-" + F.nu.v(n)
                if sType == 'NA-NA-NA': continue
                sType = sType.replace("NA-", "")
                sType = sType.replace("NA", "")
                sType = sType.replace("unknown-", "")
                sType = sType.replace("unknown", "")
                if sType == '': continue
            elif feat == 'st': sType = F.st.v(n)
            elif feat == 'vs': sType = F.vs.v(n)
            elif feat == 'vt': sType = F.vt.v(n)
            elif feat == 'function': sType = F.function.v(n)
            elif feat == 'typ': sType = F.typ.v(n)
            elif feat == 'gloss': sType = F.gloss.v(L.u(n, otype='lex')[0])
            #단어와 관련된 통계는 유의미하지 않은 요소 제거
            if feat == 'lex_utf8' or feat == 'gloss':
                if F.pdp.v(n) == 'prep': continue
                elif F.pdp.v(n)  == 'conj': continue
                elif F.pdp.v(n) == 'art': continue
                elif F.pdp.v(n) == 'nega': continue
            #키값이 있으면 기존의 키 값에 1을 더하고, 키값이 없으면 새로운 키를 생성하고 1을 부여함.
            if sType in statType:
                statType[sType] = statType[sType] + 1
            else:
                statType[sType] = 1
    sortedKey = sorted(statType, key=statType.__getitem__, reverse=True)
    i = 1
    result = OrderedDict({})
    for k in sortedKey:
        result[k] = str(statType[k])
        i = i + 1
        if i > num: break
    result['total_num'] = total_num

    return result

#1001001-1002001; 2001001-2002001 ==> Genesis, 1, 1 ~ Genesis, 2, 1; + Exodus ...
def codetorange(code):
    bookList = ["null", "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges",
            "1_Samuel", "2_Samuel", "1_Kings", "2_Kings", "Isaiah", "Jeremiah", "Ezekiel",
            "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
            "Haggai", "Zechariah", "Malachi", "Psalms", "Job", "Proverbs", "Ruth", "Song_of_songs",
            "Ecclesiastes", "Lamentations", "Esther", "Daniel", "Ezra", "Nehemiah", "1_Chronicles",
            "2_Chronicles"]
    code = code.replace(" ", "")
    codeSplit1 = code.split(';')
    nodeList = []
    last = ''
    for c1 in codeSplit1:
        i = 0
        codeSplit2 = c1.split('-')
        for c2 in codeSplit2:
            if len(c2) != 7 and len(c2) != 8:
                return False

            #book
            if len(c2) == 7:
                bookCodeList = int(c2[0])
                bookCode = bookList[bookCodeList]
            elif len(c2) == 8:
                bookCodeList = int(c2[0] + c2[1])
                bookCode = bookList[bookCodeList]
            #chapter
            chpCode = c2[-6] +  c2[-5] +  c2[-4]
            chpCode = int(chpCode)
            #verse
            verseCode = c2[-3] +  c2[-2] +  c2[-1]
            verseCode = int(verseCode)
            if i == 0:
                first = T.nodeFromSection((bookCode, chpCode, verseCode))
                i = 1
            else:
                last = T.nodeFromSection((bookCode, chpCode, verseCode))
        if(last):
            for n in range(first, last + 1):
                nodeList.append(n)
        else:
            nodeList.append(first)
    return nodeList


@app.route('/')
def main_page():
    return render_template('main.html')

@app.route('/developer/')
def developer_page():
    return render_template('developer.html')

@app.route('/license/')
def license_page():
    return render_template('license.html')

@app.route('/search_tutorial/')
def tutorial_page():
    return render_template('search_tutorial.html')

@app.route('/search_sample/')
def sample_page():
    return render_template('search_sample.html')


@app.route('/text/')
@app.route('/text/<book>')
@app.route('/text/<book>/<int:chapter>')
def text_page(book='Genesis', chapter=1):
    chpNode = T.nodeFromSection((book, chapter))
    verseNode = L.d(chpNode, otype='verse')
    whole_chpNode = T.nodeFromSection((book,))
    last_chp = T.sectionFromNode(whole_chpNode, lastSlot=True)
    verse = ""

    for v in verseNode:
        verse += '<span class=verseNode><a class=verse_num id=verse_num verse_node='+str(v)+'>'
        verse += str(T.sectionFromNode(v)[2])
        verse += ' </a>'
        wordsNode = L.d(v, otype='word')
        for w in wordsNode:
            clauseNode = L.u(w, otype='clause')
            phraseNode = L.u(w, otype='phrase')
            firstClauseWordNode = L.d(clauseNode[0], otype='word')[0]
            firstPhraseWordNode = L.d(phraseNode[0], otype='word')[0]
            lastClauseWordNode = L.d(clauseNode[0], otype='word')[-1]
            lastPhraseWordNode = L.d(phraseNode[0], otype='word')[-1]

            if w == firstClauseWordNode:
                verse += '<span class=clauseNode id=clauseNode clause_node='+str(clauseNode[0])+'>'
                verse += "<span class='syntax clause1 hidden' id=syntax>C:"+ kb.eng_to_kor(F.typ.v(clauseNode[0]), 'abbr') +"</span>"

            if w == firstPhraseWordNode:
                verse += '<span class=phraseNode id=phraseNode phrase_node='+str(phraseNode[0])+'>'
                verse += "<span class='syntax phrase1 hidden' id=syntax>P:"+ kb.eng_to_kor(F.typ.v(phraseNode[0]), 'abbr') + "," + kb.eng_to_kor(F.function.v(phraseNode[0]), 'abbr') + "</span>"

            verse += '<span class=wordNode><a tabindex=0 class=word_elm data-poload=/api/word/'+str(w)+' data-toggle=popover data-trigger=focus>'
            verse += F.g_word_utf8.v(w)
            verse += '</a></span>'

            if F.trailer_utf8.v(w):
                verse += '<span class=trailerNode>'
                verse += F.trailer_utf8.v(w)
                verse += '</span>'

            if w == lastClauseWordNode: verse += '</span>'
            if w == lastPhraseWordNode: verse += '</span>'

        verse += '</span>'

    return render_template('text.html', verse=verse, book=book, chapter=chapter, last_chp=last_chp[1])


@app.route('/api/word/<int:node>')
def show_word_function(node):
    w_f = word_function(node)
    for k, v in w_f.items():
        w_f[k] = kb.eng_to_kor(v, 'full')
    return render_template('word_api.html', w_f=w_f)

@app.route('/api/verse/<int:node>')
def show_verse_function(node):
    wordsNode = L.d(node, otype='word')
    wordsNode.reverse()
    verse_api = {'words': [], 'gloss': [], 'pdp': [], 'parse': [], 'suff': []}
    for w in wordsNode:
        verse_api['words'].append(F.g_word_utf8.v(w))
        verse_api['gloss'].append(F.gloss.v(L.u(w, otype='lex')[0]))
        pdp = kb.eng_to_kor(F.pdp.v(w), 'abbr')
        if pdp == '동':
            pdp_str = pdp + "(" + kb.eng_to_kor(F.vs.v(w), 'abbr') + ")"
            verse_api['pdp'].append(pdp_str)
            parse_str = kb.eng_to_kor(F.vt.v(w), 'abbr') + "." + kb.eng_to_kor(F.ps.v(w), 'abbr') + kb.eng_to_kor(F.gn.v(w), 'abbr') + kb.eng_to_kor(F.nu.v(w), 'abbr')
            verse_api['parse'].append(parse_str)
        elif pdp == '명':
            verse_api['pdp'].append(pdp)
            parse_str = kb.eng_to_kor(F.gn.v(w), 'abbr') + kb.eng_to_kor(F.nu.v(w), 'abbr')
            verse_api['parse'].append(parse_str)
        else:
            verse_api['pdp'].append(pdp)
            verse_api['parse'].append('')
        if F.g_prs_utf8.v(w) != "":
            suff_str = "접미." + kb.eng_to_kor(F.prs_ps.v(w), 'abbr') + kb.eng_to_kor(F.prs_gn.v(w), 'abbr') + kb.eng_to_kor(F.prs_nu.v(w), 'abbr')
            verse_api['suff'].append(suff_str)
        else:
            verse_api['suff'].append('')
    section = T.sectionFromNode(wordsNode[0])
    eng_chp_vrs = kb.heb_vrs_to_eng(section[0], str(section[1]), str(section[2]))
    verse_str = {"kjv": [], "kor": []}
    for c_v in eng_chp_vrs:
        chp_vrs = re.split(":", c_v)
        verse_str['kjv'].append(kb.json_to_verse(section[0], chp_vrs[0], chp_vrs[1], 'kjv'))
        verse_str['kor'].append(kb.json_to_verse(section[0], chp_vrs[0], chp_vrs[1], 'korean'))

    return render_template('verse_api.html', verse_api=verse_api, section=section, verse_str=verse_str)


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


@app.route('/api/stat/', methods=['GET', 'POST'])
def statistics():
    result = '<table class=table>'
    i = 0
    if request.method == 'POST':
        rangeCode = request.form['statCode']
        nodeList = codetorange(rangeCode)
        if nodeList == False: return False

        result += "<tr><td>"

        ClauseFeat = featureStat(nodeList, "clause", "typ", 10)
        totalClause = ClauseFeat['total_num']
        result += "<h4>Clause Type</h4><br>"
        for k, v in ClauseFeat.items():
            if k == "total_num": break
            propClause =round(int(v) / totalClause * 100, 2)
            result += k + ": " + str(v) + "(" + str(propClause) + "%)" + "<br>"

        result += "</td><td>"

        PhraseFeat = featureStat(nodeList, "phrase", "typ", 10)
        totalPhrase = PhraseFeat['total_num']
        result += "<h4>Phrase Type</h4><br>"
        for k, v in PhraseFeat.items():
            if k == "total_num": break
            propPhrase =round(int(v) / totalPhrase * 100, 2)
            result += k + ": " + str(v) + "(" + str(propPhrase) + "%)" + "<br>"

        result += "</td><td>"

        LexFeat = featureStat(nodeList, "word", "lex_utf8", 10)
        totalLex = LexFeat['total_num']
        result += "<h4>Word Frequency</h4><br>"
        for k, v in LexFeat.items():
            if k == "total_num": break
            propLex =round(int(v) / totalLex * 100, 2)
            result += k + ": " + str(v) + "(" + str(propLex) + "%)" + "<br>"

        result += "</td></tr><tr><td>"

        PdpFeat = featureStat(nodeList, "word", "pdp", 10)
        totalPdp = PdpFeat['total_num']
        result += "<h4>Part of Speech</h4><br>"
        for k, v in PdpFeat.items():
            if k == "total_num": break
            propPdp =round(int(v) / totalPdp * 100, 2)
            result += k + ": " + str(v) + "(" + str(propPdp) + "%)" + "<br>"

        result += "</td><td>"

        fncFeat = featureStat(nodeList, "phrase", "function", 10)
        totalfnc = fncFeat['total_num']
        result += "<h4>Phrase Function</h4><br>"
        for k, v in fncFeat.items():
            if k == "total_num": break
            propfnc =round(int(v) / totalfnc * 100, 2)
            result += k + ": " + str(v) + "(" + str(propfnc) + "%)" + "<br>"

        result += "</td><td>"

        PersonFeat = featureStat(nodeList, "word", "psgnnu", 10)
        totalPerson = PersonFeat['total_num']
        result += "<h4>Person</h4><br>"
        for k, v in PersonFeat.items():
            if k == "total_num": break
            propPerson =round(int(v) / totalPerson * 100, 2)
            result += k + ": " + str(v) + "(" + str(propPerson) + "%)" + "<br>"

        result += "</td></tr></table>"

        return result
    else:
        return render_template('stat.html')
