from flask import render_template, request, url_for
from kimsbible import app
from kimsbible.lib import index as ix

@app.route('/search/<word>', methods=['GET', 'POST'])
def search_word(word):
    indexed = ix.Indexing()
    try:
        result = indexed.search_index(word)
        print(result)
        if not result:
            result = "검색 오류"
    except:
        result = "검색 오류"
    return render_template('search.html', result=result)