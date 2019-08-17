from flask import render_template
from kimsbible import app

book_abb = {
    "Matthew": "matt",
    "Mark": "mark",
    "Luke": "luke",
    "John": "john",
    "Acts": "acts",
    "Romans": "rom",
    "1_Corinthians": "1cor",
    "2_Corinthians": "2cor",
    "Galatians": "gal",
    "Ephesians": "eph",
    "Philippians": "phil",
    "Colossians": "col",
    "1_Thessalonians": "1thess",
    "2_Thessalonians": "2thess",
    "1_Timothy": "1tim",
    "2_Timothy": "2tim",
    "Titus": "titus",
    "Philemon": "none",
    "Hebrews": "heb",
    "James": "none",
    "1_Peter": "1pet",
    "2_Peter": "2pet",
    "1_John": "none",
    "2_John": "none",
    "3_John": "none",
    "Jude": "jude",
    "Revelation": "rev" 
}


@app.route('/sblgnt/')
@app.route('/sblgnt/<book>')
@app.route('/sblgnt/<book>/<int:chapter>')
def sblgnt_page(book='Matthew', chapter=1):
    kml_file = "http://alphalef.com/apps/kml/" + book_abb[book] + '.' + str(chapter) + '.' + "kml"
    return render_template('sblgnt_text.html', book=book, chapter=chapter, kml_file=kml_file)

@app.route('/sblgnt/word/<int:node>')
def show_sblgnt_word_function(node):
    return render_template('sblgnt_word.html', node=node)

@app.route('/sblgnt/verse/<int:node>')
def show_sblgnt_verse_function(node):
    return render_template('sblgnt_verse.html', node=node)
