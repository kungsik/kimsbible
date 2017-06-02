import re

from flask import render_template
from tf.fabric import Fabric

from kimsbible import app
from kimsbible.lib.kimsbibleLib import Kimsbible as kb


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
    w_f = kb.word_function(node)
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
