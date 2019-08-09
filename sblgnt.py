from flask import render_template
from kimsbible import app

@app.route('/sblgnt/')
@app.route('/sblgnt/<book>')
@app.route('/sblgnt/<book>/<int:chapter>')
def sblgnt_page(book='Matthew', chapter=1):
    return render_template('sblgnt_text.html', book=book, chapter=chapter)

@app.route('/sblgnt/word/<int:node>')
def show_sblgnt_word_function(node):
    return render_template('sblgnt_word.html', node=node)


