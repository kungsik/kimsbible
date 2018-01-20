from tf.fabric import Fabric
from flask import render_template, request, url_for
from kimsbible import app
from kimsbible.views import api
from kimsbible.stat import codetorange
from kimsbible.stat import bookList
import math
import json

api.makeAvailableIn(globals())

def loadWordList(list):
    result = []
    for node in codetorange(list):
        wordNode = L.d(node, otype='word')
        for word in wordNode:
            if F.lex_utf8.v(word) in result: continue
            if F.pdp.v(word) == "verb" or F.pdp.v(word) == "subs":
                result.append(F.lex_utf8.v(word))
    return result

def loadWordCount(list1, list2):
    result = []
    wordData = {}

    for node in codetorange(list1):
        wordNode = L.d(node, otype='word')
        for word in wordNode:
            if F.pdp.v(word) == "verb" or F.pdp.v(word) == "subs":
                result.append(F.lex_utf8.v(word))
    for foundWord in result:
        if foundWord in wordData: continue
        occCount = result.count(foundWord)
        wordData.update({
            foundWord: {
                'tf': occCount,
                'df': 1
            }
        })
    list2data = loadWordList(list2)
    for key in wordData:
        if key in list2data:
            wordData[key]['df'] = wordData[key]['df'] + 1
    return wordData

def loadIdf(wordCount):
    idfData = {}
    resultData = {}
    for key in wordCount:
        idf = wordCount[key]['tf'] * math.log(2 / wordCount[key]['df'])
        if idf > 0:
            idf = round(idf, 5)
            idfData.update({
                key: idf
            })

    sortedData = sorted(idfData.items(), key = lambda x:x[1], reverse=True)
    return sortedData




@app.route('/tfidf/', methods=['POST','GET'])
def tfidf():
    if request.method == 'POST':
        result = []

        tfidf_1 = request.form['tfidf_1']
        tfidf_2 = request.form['tfidf_2']

        wordCount_1 = loadWordCount(tfidf_1, tfidf_2)
        wordCount_2 = loadWordCount(tfidf_2, tfidf_1)

        result_1 = loadIdf(wordCount_1)
        result_2 = loadIdf(wordCount_2)

        result.append(result_1)
        result.append(result_2)

        return json.dumps(result)

    else:
        return render_template('tfidf.html')
