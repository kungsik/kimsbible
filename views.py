import re
import os
from collections import OrderedDict


from flask import render_template, request, url_for
from tf.fabric import Fabric

from kimsbible import app
from kimsbible.lib import lib as kb

### Load up TF ###
ETCBC = 'hebrew/etcbc4c'
TF = Fabric(locations='text-fabric-data', modules=ETCBC)
#api = TF.load('book')

api = TF.load('''
    book chapter verse
    nu gn ps vt vs st
    otype typ function
    det pdp qere_utf8 qere_trailer_utf8
    g_word_utf8 trailer_utf8
    lex_utf8 lex voc_utf8
    g_prs_utf8 g_uvf_utf8
    prs_gn prs_nu prs_ps g_cons_utf8
    gloss phono
''')

api.makeAvailableIn(globals())

book_abb = {
    "Genesis": "gen",
    "Exodus": "exod",
    "Leviticus": "lev",
    "Numbers": "num",
    "Deuteronomy": "deut",
    "Joshua": "josh",
    "Judges": "judg",
    "1_Samuel": "1sam",
    "2_Samuel": "2sam",
    "1_Kings": "1kgs",
    "2_Kings": "2kgs",
    "Isaiah": "isa",
    "Jeremiah": "jer",
    "Ezekiel": "ezek",
    "Hosea": "hos",
    "Joel": "joel",
    "Amos": "amos",
    "Obadiah": "obad",
    "Jonah": "jonah",
    "Micah": "mic",
    "Nahum": "nah",
    "Habakkuk": "hab",
    "Zephaniah": "zeph",
    "Haggai": "hag",
    "Zechariah": "zech",
    "Malachi": "mal",
    "Psalms": "ps",
    "Job": "job",
    "Proverbs": "none",
    "Ruth": "ruth",
    "Song_of_songs": "song",
    "Ecclesiastes": "eccl",
    "Lamentations": "lam",
    "Esther": "esth",
    "Daniel": "dan",
    "Ezra": "ezra",
    "Nehemiah": "neh",
    "1_Chronicles": "1chr",
    "2_Chronicles": "2chr"
}

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
    w_f["의미"] = w_f["의미"].replace('<', '[').replace('>', ']')
    w_f["사전"] = "<a href='http://dict.naver.com/hbokodict/ancienthebrew/#/search?query=" + w_f["원형"] + "' target=_blank>보기</a>"
    w_f["용례"] = "<a href='/api/search/?cons=" + F.lex_utf8.v(node) + "&sp=" + w_f["품사"] + "' target=_blank>검색</a>"

    if w_f["동사형"] != "NA" and w_f["동사형"] != "" and w_f["동사형"] != "unknown":
        w_f["동사형태"] = "<a href='/conjugator/?cons=" + w_f["원형"] + "' target=_blank>검색</a>"

    return w_f

@app.route('/')
def main_page():
    return render_template('main.html')

@app.route('/developer/')
def developer_page():
    return render_template('developer.html')

@app.route('/license/')
def license_page():
    return render_template('license.html')

@app.route('/community/')
def community_page():
    return render_template('community.html')

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

            if F.qere_utf8.v(w):
                verse += '<span class=wordNode>'
                verse += F.g_word_utf8.v(w) + ' '
                verse += '</a></span>'

                verse += '<span class=wordNode><a tabindex=0 class=word_elm data-poload=/api/word/'+str(w)+' data-toggle=popover data-trigger=focus>'
                verse += F.qere_utf8.v(w)
                verse += '</a></span>'

                if F.qere_trailer_utf8.v(w):
                    verse += '<span class=trailerNode>'
                    verse += F.qere_trailer_utf8.v(w)
                    verse += '</span>'

            else:
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

        section = T.sectionFromNode(v)
        eng_chp_vrs = kb.heb_vrs_to_eng(section[0], str(section[1]), str(section[2]))
        for c_v in eng_chp_vrs:
            chp_vrs = re.split(":", c_v)
            kor_vrs = kb.json_to_verse(section[0], chp_vrs[0], chp_vrs[1], 'korean')

        #verse += "<p class='alert alert-warning korean' dir=ltr align=left>" + kor_vrs + "</p>"
        verse += "<p class='heb_korean' id='heb_korean' dir=ltr align=left>" + kor_vrs + "</p>"

        kml_file = "http://alphalef.com/apps/kml/" + book_abb[book] + '.' + str(chapter) + '.' + "kml"

    return render_template('text.html', verse=verse, book=book, chapter=chapter, last_chp=last_chp[1], kml_file=kml_file)


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
