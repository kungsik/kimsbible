from tf.fabric import Fabric
from flask import render_template, request, url_for
from kimsbible import app
from kimsbible.bhsheb import api
from kimsbible.bhsheb import get_strong, get_kor_hgloss
from collections import OrderedDict
from kimsbible.lib import lib as kb

api.makeAvailableIn(globals())

bookList = ["null", "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges",
        "1_Samuel", "2_Samuel", "1_Kings", "2_Kings", "Isaiah", "Jeremiah", "Ezekiel",
        "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
        "Haggai", "Zechariah", "Malachi", "Psalms", "Job", "Proverbs", "Ruth", "Song_of_songs",
        "Ecclesiastes", "Lamentations", "Esther", "Daniel", "Ezra", "Nehemiah", "1_Chronicles",
        "2_Chronicles"]

bookListKor = ["null", "창세기", "출애굽기", "레위기", "민수기", "신명기", "여호수아", "사사기", 
        "사무엘상", "사무엘하", "열왕기상", "열왕기하", "이사야", "예레미야", "에스겔", 
        "호세아", "요엘", "아모스", "오바댜", "요나", "미가", "나훔", "하박국", "스바냐", 
        "학개", "스가랴", "말라기", "시편", "욥기", "잠언", "룻기", "아가",
        "전도서", "예레미야애가", "에스더", "다니엘", "에스라", "느헤미야", "역대상", 
        "역대하"]

bookListKorAbbr = ["null", "창", "출", "레", "민", "신", "수", "삿", "삼상", "삼하", "왕상", "왕하",
        "사", "렘", "겔", "호", "욜", "암", "옵", "욘", "미", "나", "합", "습", "학", "슥", "말",
        "시", "욥", "잠", "룻", "아", "전", "애", "에", "단", "스", "느", "대상", "대하"]


def booknameconv(v, book1, book2):
    num = book1.index(v)
    return book2[num] 

def codetostr(code, bookList):
    code = code.replace(" ", "")
    codeSplit1 = code.split(';')
    strvrs = ""
    i = 0
    for c1 in codeSplit1:
        codeSplit2 = c1.split('-')
        if i > 0:
            strvrs += "; "
            i = 0

        for c2 in codeSplit2:
            if len(c2) != 7 and len(c2) != 8:
                return False
            if i == 1:
                strvrs += "~"
            if len(c2) == 7:
                strvrs += bookList[int(c2[0])] + " " + str(int(c2[-6] +  c2[-5] +  c2[-4])) + ":" + str(int(c2[-3] +  c2[-2] +  c2[-1]))
            elif len(c2) == 8:
                strvrs += bookList[int(c2[0] + c2[1])] + " " + str(int(c2[-6] +  c2[-5] +  c2[-4])) + ":" + str(int(c2[-3] +  c2[-2] +  c2[-1]))
            i = i + 1
    return strvrs


#1001001-1002001; 2001001-2002001 ==> Genesis, 1, 1 ~ Genesis, 2, 1; + Exodus ...
def codetorange(code):
    code = code.replace(" ", "")
    codeSplit1 = code.split(';')
    nodeList = []
    for c1 in codeSplit1:
        codeSplit2 = c1.split('-')
        i = 0
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
                if len(codeSplit2) < 2:
                    nodeList.append(first)
            else:
                last = T.nodeFromSection((bookCode, chpCode, verseCode))
                for n in range(first, last + 1):
                    nodeList.append(n)    
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

@app.route('/bhsheb/stat/tutorial/')
def stat_tutorial():
    return render_template('bhsheb_stat_tutorial.html')


@app.route('/bhsheb/stat/', methods=['GET', 'POST'])
def statistics():
    i = 0
    if request.method == 'POST':
        rangeCode = request.form['statCode']
        nodeList = codetorange(rangeCode)
        rangestr = codetostr(rangeCode, bookListKor)
        if nodeList == False: return False

        result = "<h4>" + rangestr + "</h4>"
        result += '<br><table class=table>'
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
        result += "<h4>Word Frequency</h4><br><div style='direction:rtl; text-align:left'>"
        for k, v in LexFeat.items():
            if k == "total_num": break
            propLex =round(int(v) / totalLex * 100, 2)
            result += k + ": " + str(v) + "(" + str(propLex) + "%)" + "<br>"

        result += "</div></td></tr><tr><td>"

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
        return render_template('bhsheb_stat.html')

# 파싱 데이터 - 맛사 제공
@app.route('/api/parsing/', methods=['GET', 'POST'])
@app.route('/bhsheb/parsing/', methods=['GET', 'POST'])
def parsing():
    if request.method == 'POST':
        rangeCode = request.form['parsingCode']
        nodeList = codetorange(rangeCode)
        rangeStr = codetostr(rangeCode, bookListKor)
        
        if nodeList == False: return False
        result = "<h4>" + rangeStr + "</h4>"

        result += "<div>"
        for verseNode in nodeList:
            result += booknameconv(str(T.sectionFromNode(verseNode)[0]), bookList, bookListKorAbbr) + str(T.sectionFromNode(verseNode)[1]) + ":" + str(T.sectionFromNode(verseNode)[2]) + " "
            wordNode = L.d(verseNode, otype = 'word')
            for n in wordNode:
                result += "<span>"
                result += "[" + F.g_word_utf8.v(n) + "] "

                strong = get_strong(n)
                gloss = get_kor_hgloss(strong, n)
                result += gloss + " "
                # result += F.gloss.v(L.u(n, otype='lex')[0]).replace("<", "").replace(">", "") + " "
                
                if F.pdp.v(n) == "verb":
                    result += "(" + F.voc_utf8.v(L.u(n, otype='lex')[0]) + ") "
                    result += kb.eng_to_kor(F.vs.v(n), 'abbr') + "." + kb.eng_to_kor(F.vt.v(n), 'abbr') + "." + kb.eng_to_kor(F.ps.v(n), 'abbr') + kb.eng_to_kor(F.gn.v(n), 'abbr') + kb.eng_to_kor(F.nu.v(n), 'abbr') + " "
                    if F.prs_ps.v(n) != 'unknown':
                        result += "접미."
                        result += kb.eng_to_kor(F.prs_ps.v(n), 'abbr') + kb.eng_to_kor(F.prs_gn.v(n), 'abbr') + kb.eng_to_kor(F.prs_nu.v(n), 'abbr') + " "

                result += "</span>"
            result += "<br>"
        result += "</div>"
        return result

    else:
        return render_template('bhsheb_parsing.html')

 
