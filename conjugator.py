from tf.fabric import Fabric
from flask import render_template, request, url_for
from kimsbible import app
from kimsbible.views import api
import json

api.makeAvailableIn(globals())

def sortkeypicker(keynames):
    negate = set()
    for i, k in enumerate(keynames):
        if k[:1] == '-':
            keynames[i] = k[1:]
            negate.add(k[1:])
    def getit(adict):
       composite = [adict[k] for k in keynames]
       for i, (k, v) in enumerate(zip(keynames, composite)):
           if k in negate:
               composite[i] = -v
       return composite
    return getit

def verbaldata(verb):
    verb = verb.replace('שׁ', 'שׁ').replace('שׂ', 'שׂ')
    verb = verb.replace('ם','מ').replace('ך','כ').replace('ן','נ').replace('ף','פ').replace('ץ','צ')
    verb = verb.replace('ש1', 'שׁ').replace('ש2', 'שׂ')
    query = "word lex_utf8="+verb
    S.search(query)
    fetch_data = list(S.fetch())

    if len(fetch_data) == 0:
        return False

    i = 0
    wordlist = {}
    wholelist = []
    checklist = []
    for w in fetch_data:
        node = w[0]
        if F.ps.v(node) == "unknown":
            ps = ''
        else:
            ps = F.ps.v(node)

        if F.gn.v(node) == "unknown":
            gn = ''
        else:
            gn = F.gn.v(node)

        if F.nu.v(node) == "unknown":
            nu = ''
        else:
            nu = F.nu.v(node)

        if F.prs_ps.v(node) == "unknown":
            prs_ps = ''
        else:
            prs_ps = F.prs_ps.v(node)

        if F.prs_gn.v(node) == "unknown":
            prs_gn = ''
        else:
            prs_gn = F.prs_gn.v(node)

        if F.prs_nu.v(node) == "unknown":
            prs_nu = ''
        else:
            prs_nu = F.prs_nu.v(node)

        checkvalue = F.vs.v(node) + F.vt.v(node) + ps + gn + nu + prs_ps + prs_gn + prs_nu
        if F.pdp.v(node) != "verb" or checkvalue in checklist:
            continue
        else:
            if F.vs.v(node) == 'hif' or F.vs.v(node) == 'hit' or F.vs.v(node) == 'htpo' or F.vs.v(node) == 'hof' or F.vs.v(node) == 'nif':
                lang= "Heb"
            elif F.vs.v(node) == 'piel' or F.vs.v(node) == 'poal' or F.vs.v(node) == 'poel' or F.vs.v(node) == 'pual' or F.vs.v(node) == 'qal':
                lang = "Heb"
            else:
                lang = "Arm"

            if F.vt.v(node) == 'wayq':
                verb = F.g_word_utf8.v(node-1) + F.g_word_utf8.v(node)
            else:
                verb = F.g_word_utf8.v(node)

            query = "<a href=/api/search/?cons=" + F.lex_utf8.v(node) + "&tense=" + F.vt.v(node) + "&stem=" + F.vs.v(node)
            query += "&ps=" + F.ps.v(node)
            query += "&gn=" + F.gn.v(node)
            query += "&nu=" + F.nu.v(node)
            query += "&prs_ps=" + F.prs_ps.v(node)
            query += "&prs_gn=" + F.prs_gn.v(node)
            query += "&prs_nu=" + F.prs_nu.v(node)
            query += " target=_blank>검색</a>"

            wordlist = {
                "lang": lang,
                "verb": verb,
                "stem":F.vs.v(node),
                "tense":F.vt.v(node),
                "ps":ps,
                "gn":gn,
                "nu":nu,
                "prs_ps":prs_ps,
                "prs_gn":prs_gn,
                "prs_nu":prs_nu,
                "query": query
            }
            wholelist.append(wordlist)
            checklist.append(F.vs.v(node) + F.vt.v(node) + ps + gn + nu + prs_ps + prs_gn + prs_nu)
            i = i + 1

    if i == 0: return False

    sortedlist = sorted(wholelist, key=sortkeypicker(['lang', 'stem', 'tense', 'ps', 'gn', 'nu', 'prs_ps', 'prs_gn', 'prs_nu']))

    return sortedlist


@app.route('/conjugator/', methods=['GET', 'POST'])
def conjugator():
    if request.method == 'POST':
        verb = request.form['verb']
        result = verbaldata(verb)
        return json.dumps(result)
    else:
        return render_template('conjugator.html')
