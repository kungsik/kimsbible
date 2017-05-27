from flask import Flask, render_template
from kimsbible import app
from tf.fabric import Fabric

### Load up TF ###
ETCBC = 'hebrew/etcbc4c'
TF = Fabric(modules=ETCBC)
api = TF.load('''
    sp lex voc_utf8
    g_word trailer
    qere qere_trailer
    language freq_lex gloss
    mother
''')
api.makeAvailableIn(globals())

@app.context_processor
def utility_processor():
    def view_text_line(book, chapter):
        chpNode = T.nodeFromSection((book, chapter))
        verseNodes = L.d(chpNode, otype='verse')
        verse_show = dict()
        for v in verseNodes:
            verseNum = T.sectionFromNode(v)[2]
            verseTxt = T.text(L.d(v, otype='word'))
            verse_show.update({verseNum:verseTxt})
        return verse_show
    return dict(view_text_line=view_text_line)


@app.route('/')
@app.route('/<book>/')
@app.route('/<book>/<int:chapter>')
def main_page(book='Genesis', chapter=1):
    return render_template('main.html', book=book, chapter=chapter)
