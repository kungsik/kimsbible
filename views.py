from flask import Flask, render_template
from kimsbible import app
from tf.fabric import Fabric

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
    gloss g_lex_utf8
''')
api.makeAvailableIn(globals())

@app.route('/')
@app.route('/<book>/')
@app.route('/<book>/<int:chapter>')
def main_page(book='Genesis', chapter=1):
    chpNode = T.nodeFromSection((book, chapter))
    verseNode = L.d(chpNode, otype='verse')
    verse = ""
    for v in verseNode:
        verse += '<span class=verse_num>'
        verse += str(T.sectionFromNode(v)[2])
        verse += '</span>'
        wordsNode = L.d(v, otype='word')
        for w in wordsNode:
            verse += '<span class=word_elm word_node='+str(w)+'>'
            verse += F.g_word_utf8.v(w)
            verse += '</span>'
            if F.trailer_utf8.v(w):
                verse += '<span class=trailer>'
                verse += F.trailer_utf8.v(w)
                verse += '</span>'
    return render_template('main.html', verse=verse, book=book, chapter=chapter)


@app.route('/api/word/<int:node>')
def show_word_function(node):
    word_function = {
        "tricons": F.lex_utf8.v(node).replace('=', '').replace('/', '').replace('[', ''),
        "lex": F.lex.v(node),
        "voc_utf8": F.voc_utf8.v(L.u(node, otype='lex')[0]),
        "sp": F.sp.v(node), # part of speech (verb, subs ..)
        "ps": F.ps.v(node), # person (p1, p2, p3)
        "nu": F.nu.v(node), # number (sg, pl, du)
        "gn": F.gn.v(node), # gender
        "vt": F.vt.v(node),  # vt = verbal tense
        "vs": F.vs.v(node),  # vs = verbal stem
        "st": F.st.v(node),  # construct/absolute/emphatic
        "is_definite": F.det.v(L.u(node, otype='phrase_atom')[0]),
        "g_prs_utf8": F.g_prs_utf8.v(node), #pronominal suffix in Heb
        "g_uvf_utf8": F.g_uvf_utf8.v(node), #univalent final in Heb
        "g_cons_utf8": F.g_cons_utf8.v(node),
        "prs_nu": F.prs_nu.v(node), #pronominal suffix number
        "prs_gn": F.prs_gn.v(node), #pronominal suffix gender
        "prs_ps": F.prs_ps.v(node), #pronominal suffix person
        "has_suffix": "Yes" if F.g_prs_utf8.v(node) != "" else "No",
        "gloss": F.gloss.v(L.u(node, otype='lex')[0]),
        "g_lex_utf8": F.g_lex_utf8.v(node),
        "lex_utf8": F.lex_utf8.v(node),
    }
    return render_template('word_api.html', word_function=word_function)