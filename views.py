from flask import Flask, render_template
from kimsbible import app
from tf.fabric import Fabric

### Load up TF ###
ETCBC = 'hebrew/etcbc4c'
TF = Fabric(modules=ETCBC)
api = TF.load('''
    book chapter verse
    sp nu gn ps vt vs st
    otype
    det
    g_word_utf8 trailer_utf8
    lex_utf8 lex voc_utf8
    g_prs_utf8 g_uvf_utf8
    prs_gn prs_nu prs_ps g_cons_utf8
    gloss 
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
            verse += '<span class=word_elm>'
            verse += F.g_word_utf8.v(w)
            verse += '</span>'
            if F.trailer_utf8.v(w):
                verse += '<span class=trailer>'
                verse += F.trailer_utf8.v(w)
                verse += '</span>'
    return render_template('main.html', verse=verse, book=book, chapter=chapter)

