from tf.fabric import Fabric
from flask import render_template, request, url_for
from kimsbible import app
from kimsbible.views import api
from collections import OrderedDict

api.makeAvailableIn(globals())

#1001001-1002001; 2001001-2002001 ==> Genesis, 1, 1 ~ Genesis, 2, 1; + Exodus ...
def codetorange(code):
    bookList = ["null", "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges",
            "1_Samuel", "2_Samuel", "1_Kings", "2_Kings", "Isaiah", "Jeremiah", "Ezekiel",
            "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
            "Haggai", "Zechariah", "Malachi", "Psalms", "Job", "Proverbs", "Ruth", "Song_of_songs",
            "Ecclesiastes", "Lamentations", "Esther", "Daniel", "Ezra", "Nehemiah", "1_Chronicles",
            "2_Chronicles"]
    code = code.replace(" ", "")
    codeSplit1 = code.split(';')
    nodeList = []
    last = ''
    for c1 in codeSplit1:
        i = 0
        codeSplit2 = c1.split('-')
        for c2 in codeSplit2:
            if len(c2) != 7 and len(c2) != 8:
                return False

            #book
            if len(c2) == 7:
                bookCodeList = int(c2[0])
                bookCode = bookList[bookCodeList]
            elif len(c2) == 8:
                bookCodeList = int(c2[0] + c2[1])
                bookCode = bookList[bookCodeList]
            #chapter
            chpCode = c2[-6] +  c2[-5] +  c2[-4]
            chpCode = int(chpCode)
            #verse
            verseCode = c2[-3] +  c2[-2] +  c2[-1]
            verseCode = int(verseCode)
            if i == 0:
                first = T.nodeFromSection((bookCode, chpCode, verseCode))
                i = 1
            else:
                last = T.nodeFromSection((bookCode, chpCode, verseCode))
        if(last):
            for n in range(first, last + 1):
                nodeList.append(n)
        else:
            nodeList.append(first)
    return nodeList


#node: 범위값; synType: clause, phrase, word; feat: 문법요소; num: 상위 몇개까지 줄력할지.
def featureStat(node, synType, feat, num):
    statType = {}
    total_num = 0
    for verseNode in node:
        statNode = L.d(verseNode, otype = synType)
        for n in statNode:
            total_num = total_num + 1

            if total_num > 40000: return False

            if feat == 'lex_utf8': sType = F.lex_utf8.v(L.u(n, otype='lex')[0])
            elif feat == 'pdp': sType = F.pdp.v(n)
            elif feat == 'psgnnu':
                sType = F.ps.v(n) + "-" + F.gn.v(n) + "-" + F.nu.v(n)
                if sType == 'NA-NA-NA': continue
                sType = sType.replace("NA-", "")
                sType = sType.replace("NA", "")
                sType = sType.replace("unknown-", "")
                sType = sType.replace("unknown", "")
                if sType == '': continue
            elif feat == 'st': sType = F.st.v(n)
            elif feat == 'vs': sType = F.vs.v(n)
            elif feat == 'vt': sType = F.vt.v(n)
            elif feat == 'function': sType = F.function.v(n)
            elif feat == 'typ': sType = F.typ.v(n)
            elif feat == 'gloss': sType = F.gloss.v(L.u(n, otype='lex')[0])
            #단어와 관련된 통계는 유의미하지 않은 요소 제거
            if feat == 'lex_utf8' or feat == 'gloss':
                if F.pdp.v(n) == 'prep': continue
                elif F.pdp.v(n)  == 'conj': continue
                elif F.pdp.v(n) == 'art': continue
                elif F.pdp.v(n) == 'nega': continue
            #키값이 있으면 기존의 키 값에 1을 더하고, 키값이 없으면 새로운 키를 생성하고 1을 부여함.
            if sType in statType:
                statType[sType] = statType[sType] + 1
            else:
                statType[sType] = 1
    sortedKey = sorted(statType, key=statType.__getitem__, reverse=True)
    i = 1
    result = OrderedDict({})
    for k in sortedKey:
        result[k] = str(statType[k])
        i = i + 1
        if i > num: break
    result['total_num'] = total_num

    return result


@app.route('/api/stat/', methods=['GET', 'POST'])
def statistics():
    result = '<table class=table>'
    i = 0
    if request.method == 'POST':
        rangeCode = request.form['statCode']
        nodeList = codetorange(rangeCode)
        if nodeList == False: return False

        result += "<tr><td>"

        ClauseFeat = featureStat(nodeList, "clause", "typ", 10)
        totalClause = ClauseFeat['total_num']
        result += "<h4>Clause Type</h4><br>"
        for k, v in ClauseFeat.items():
            if k == "total_num": break
            propClause =round(int(v) / totalClause * 100, 2)
            result += k + ": " + str(v) + "(" + str(propClause) + "%)" + "<br>"

        result += "</td><td>"

        PhraseFeat = featureStat(nodeList, "phrase", "typ", 10)
        totalPhrase = PhraseFeat['total_num']
        result += "<h4>Phrase Type</h4><br>"
        for k, v in PhraseFeat.items():
            if k == "total_num": break
            propPhrase =round(int(v) / totalPhrase * 100, 2)
            result += k + ": " + str(v) + "(" + str(propPhrase) + "%)" + "<br>"

        result += "</td><td>"

        LexFeat = featureStat(nodeList, "word", "lex_utf8", 10)
        totalLex = LexFeat['total_num']
        result += "<h4>Word Frequency</h4><br>"
        for k, v in LexFeat.items():
            if k == "total_num": break
            propLex =round(int(v) / totalLex * 100, 2)
            result += k + ": " + str(v) + "(" + str(propLex) + "%)" + "<br>"

        result += "</td></tr><tr><td>"

        PdpFeat = featureStat(nodeList, "word", "pdp", 10)
        totalPdp = PdpFeat['total_num']
        result += "<h4>Part of Speech</h4><br>"
        for k, v in PdpFeat.items():
            if k == "total_num": break
            propPdp =round(int(v) / totalPdp * 100, 2)
            result += k + ": " + str(v) + "(" + str(propPdp) + "%)" + "<br>"

        result += "</td><td>"

        fncFeat = featureStat(nodeList, "phrase", "function", 10)
        totalfnc = fncFeat['total_num']
        result += "<h4>Phrase Function</h4><br>"
        for k, v in fncFeat.items():
            if k == "total_num": break
            propfnc =round(int(v) / totalfnc * 100, 2)
            result += k + ": " + str(v) + "(" + str(propfnc) + "%)" + "<br>"

        result += "</td><td>"

        PersonFeat = featureStat(nodeList, "word", "psgnnu", 10)
        totalPerson = PersonFeat['total_num']
        result += "<h4>Person</h4><br>"
        for k, v in PersonFeat.items():
            if k == "total_num": break
            propPerson =round(int(v) / totalPerson * 100, 2)
            result += k + ": " + str(v) + "(" + str(propPerson) + "%)" + "<br>"

        result += "</td></tr></table>"

        return result
    else:
        return render_template('stat.html')
