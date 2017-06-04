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
    sp nu gn ps vt vs st
    otype
    det
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
    w_f["품사"] = F.sp.v(node)  # part of speech (verb, subs ..)
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

@app.route('/')
def main_page():
    return render_template('main.html')

@app.route('/developer/')
def developer_page():
    return render_template('developer.html')

@app.route('/license/')
def license_page():
    return render_template('license.html')

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
        verse += '<span class=verse_num verse_node='+str(v)+'>'
        verse += str(T.sectionFromNode(v)[2])
        verse += ' </span>'
        wordsNode = L.d(v, otype='word')
        for w in wordsNode:
            verse += '<a tabindex=0 class=word_elm data-poload=/api/word/'+str(w)+' data-toggle=popover data-trigger=focus>'
            verse += F.g_word_utf8.v(w)
            verse += '</a>'
            if F.trailer_utf8.v(w):
                verse += '<span class=trailer>'
                verse += F.trailer_utf8.v(w)
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
    verse_api = {'words': [], 'gloss': [], 'sp': [], 'parse': [], 'suff': []}
    for w in wordsNode:
        verse_api['words'].append(F.g_word_utf8.v(w))
        verse_api['gloss'].append(F.gloss.v(L.u(w, otype='lex')[0]))
        sp = kb.eng_to_kor(F.sp.v(w), 'abbr')
        if sp == '동':
            sp_str = sp + "(" + kb.eng_to_kor(F.vs.v(w), 'abbr') + ")"
            verse_api['sp'].append(sp_str)
            parse_str = kb.eng_to_kor(F.vt.v(w), 'abbr') + "." + kb.eng_to_kor(F.ps.v(w), 'abbr') + kb.eng_to_kor(F.gn.v(w), 'abbr') + kb.eng_to_kor(F.nu.v(w), 'abbr')
            verse_api['parse'].append(parse_str)
        elif sp == '명':
            verse_api['sp'].append(sp)
            parse_str = kb.eng_to_kor(F.gn.v(w), 'abbr') + kb.eng_to_kor(F.nu.v(w), 'abbr')
            verse_api['parse'].append(parse_str)
        else:
            verse_api['sp'].append(sp)
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
        S.search(query)
        result = "<table class='paginated'><tbody>"
        i = 0
        for r in S.fetch(limit=100):
            i = int(i)
            i = i + 1
            result += "<tr><td>" + str(i) + ":  </td><td>"+S.glean(r)+"</td></tr>"
        result += "</tbody></table>"
        if i == 0:
            return False
        else:
            return result
    else:
        return render_template('search.html')
