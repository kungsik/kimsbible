import json
import codecs
import os
import re
from collections import OrderedDict

from flask import render_template
from tf.fabric import Fabric

from kimsbible import app

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
    gloss g_lex_utf8 phono
''')
api.makeAvailableIn(globals())

#외부 API를 이용한 번역본 인용.
'''
def json_to_verse(book, chp, verse, ver):
    url = "https://getbible.net/json?passage=" + book + "_" + chp + ":" + verse + "&version=" + ver
    with urllib.request.urlopen(url) as u:
        data = u.read().decode().replace('(', '').replace(');', '')
        verse_json = json.loads(data)
        verse_str = chp + ":" + verse + " " + verse_json['book'][0]['chapter'][verse]['verse']
        return verse_str
'''
#자체 json 파일로 번역본 인용
def json_to_verse(book, chp, verse, ver):
    path = os.path.dirname(os.path.abspath(__file__))
    location = path + "/static/json/" + ver + ".json"
    book_code = {
        "Genesis": 0,
        "Exodus": 1,
        "Leviticus": 2,
        "Numbers": 3,
        "Deuteronomy": 4,
        "Joshua": 5,
        "Judges": 6,
        "Ruth": 7,
        "1_Samuel": 8,
        "2_Samuel": 9,
        "1_Kings": 10,
        "2_Kings": 11,
        "1_Chronicles": 12,
        "2_Chronicles": 13,
        "Ezra": 14,
        "Nehemiah": 15,
        "Esther": 16,
        "Job": 17,
        "Psalms": 18,
        "Proverbs": 19,
        "Ecclesiastes": 20,
        "Song_of_songs": 21,
        "Isaiah": 22,
        "Jeremiah": 23,
        "Lamentations": 24,
        "Ezekiel": 25,
        "Daniel": 26,
        "Hosea": 27,
        "Joel": 28,
        "Amos": 29,
        "Obadiah": 30,
        "Jonah": 31,
        "Micah": 32,
        "Nahum": 33,
        "Habakkuk": 34,
        "Zephaniah": 35,
        "Haggai": 36,
        "Zechariah": 37,
        "Malachi": 38,
    }
    with codecs.open(location, 'r', 'utf-8-sig') as json_data:
        d = json.load(json_data)
        json_chp = int(chp) - 1
        verse_str = chp + ":" + verse + " " + d[book_code[book]]['chapters'][json_chp][chp][verse]
        return verse_str

def heb_vrs_to_eng(book, chp, verse):
    vrs_str = chp + ":" + verse
    path = os.path.dirname(os.path.abspath(__file__))
    location = path + "/static/json/heb_eng_vrs.json"
    with open(location) as json_data:
        d = json.load(json_data)
        if book in d.keys():
            if vrs_str in d[book].keys():
                if isinstance(d[book][vrs_str], list):
                    eng_chp_vrs = d[book][vrs_str]
                    return eng_chp_vrs
                else:
                    eng_chp_vrs = [d[book][vrs_str]]
                    return eng_chp_vrs
            else:
                eng_chp_vrs = [chp+":"+verse]
                return eng_chp_vrs
        else:
            eng_chp_vrs = [chp + ":" + verse]
            return eng_chp_vrs

translate = {
    "art": {"full": "관사", "abbr": "관"},
    "verb": {"full": "동사", "abbr": "동"},
    "subs": {"full": "명사", "abbr": "명"},
    "nmpr": {"full": "고유명사", "abbr": "고명"},
    "advb": {"full": "부사", "abbr": "부"},
    "prep": {"full": "전치사", "abbr": "전"},
    "conj": {"full": "접속사", "abbr": "접"},
    "prps": {"full": "인칭대명사", "abbr": "인대"},
    "prde": {"full": "지시대명사", "abbr": "지대"},
    "prin": {"full": "의문대명사", "abbr": "의대"},
    "intj": {"full": "감탄사", "abbr": "감탄"},
    "nega": {"full": "부정", "abbr": "부정"},
    "inrg": {"full": "의문사", "abbr": "의문"},
    "adjv": {"full": "형용사", "abbr": "형"},
    "sg": {"full": "단수", "abbr": "단"},
    "du": {"full": "쌍수", "abbr": "쌍"},
    "pl": {"full": "복수", "abbr": "복"},
    "m": {"full": "남성", "abbr": "남"},
    "f": {"full": "여성", "abbr": "여"},
    "p1": {"full": "1인칭", "abbr": "1"},
    "p2": {"full": "2인칭", "abbr": "2"},
    "p3": {"full": "3인칭", "abbr": "3"},
    "perf": {"full": "완료형", "abbr": "완"},
    "impf": {"full": "미완료형", "abbr": "미완"},
    "wayq": {"full": "봐이크톨", "abbr": "봐잌"},
    "impv": {"full": "명령형", "abbr": "명령"},
    "infa": {"full": "부정사 절대형", "abbr": "부절"},
    "infc": {"full": "부정사 연계형", "abbr": "부연"},
    "ptca": {"full": "능동분사", "abbr": "능분"},
    "ptcp": {"full": "수동분사", "abbr": "수분"},
    "hif": {"full": "Hif‘il(H)", "abbr": "Hif‘il"},
    "hit": {"full": "Hitpa“el(H)", "abbr": "Hitpa“el"},
    "htpo": {"full": "Hitpo“el(H)", "abbr": "Hitpo“el"},
    "hof": {"full": "Hof‘al(H)", "abbr": "Hof‘al"},
    "nif": {"full": "Nif‘al(H)", "abbr": "Nif‘al"},
    "piel": {"full": "Pi“el(H)", "abbr": "Pi“el"},
    "poal": {"full": "Po“al(H)", "abbr": "Po“al"},
    "poel": {"full": "Po“el(H)", "abbr": "Po“el"},
    "pual": {"full": "Pu“al(H)", "abbr": "Pu“al"},
    "qal": {"full": "Qal(H)", "abbr": "Qal"},
    "afel": {"full": "Af‘el(Ar)", "abbr": "Af‘el"},
    "etpa": {"full": "Etpa“al(Ar)", "abbr": "Etpa“al"},
    "etpe": {"full": "Etpe‘el(Ar)", "abbr": "Etpe‘el"},
    "haf": {"full": "Haf‘el(Ar)", "abbr": "Haf‘el"},
    "hotp": {"full": "Hotpa“al(Ar)", "abbr": "Hotpa“al"},
    "hsht": {"full": "Hishtaf‘al(Ar)", "abbr": "Hishtaf‘al"},
    "htpa": {"full": "Hitpa“al(Ar)", "abbr": "Hitpa“al"},
    "htpe": {"full": "Hitpe‘el(Ar)", "abbr": "Hitpe‘el"},
    "nit": {"full": "Nitpa“el(Ar)", "abbr": "Nitpa“el"},
    "pael": {"full": "Pa“el(Ar)", "abbr": "Pa“el"},
    "peal": {"full": "Pe‘al(Ar)", "abbr": "Pe‘al"},
    "peil": {"full": "Pe‘il(Ar)", "abbr": "Pe‘il"},
    "shaf": {"full": "Shaf‘el(Ar)", "abbr": "Shaf‘el"},
    "tif": {"full": "Tif‘al(Ar)", "abbr": "Tif‘al"},
    "pasq": {"full": "Passiveqal(Ar)", "abbr": "Passiveqal"},
    "a": {"full": "절대형", "abbr": "절대"},
    "c": {"full": "연계형", "abbr": "연계"},
    "e": {"full": "강조형", "abbr": "강조"},
    "AjCl": {"full": "형용사절", "abbr": "형절"},
    "CPen": {"full": "Casus pendens", "abbr": "CP"},
    "Defc": {"full": "불완전절", "abbr": "불완"},
    "Ellp": {"full": "생략", "abbr": "생략"},
    "InfA": {"full": "절대형부정사절", "abbr": "절부"},
    "InfC": {"full": "연계형부정사절", "abbr": "연부"},
    "MSyn": {"full": "매크로구문표시", "abbr": "매크"},
    "NmCl": {"full": "명사절", "abbr": "명절"},
    "Ptcp": {"full": "분사절", "abbr": "분절"},
    "Reop": {"full": "재개", "abbr": "재개"},
    "Voct": {"full": "호격절", "abbr": "호격"},
    "Way0": {"full": "Wayyiqtol-null clause", "abbr": "Way0"},
    "WayX": {"full": "Wayyiqtol-X clause", "abbr": "WayX"},
    "WIm0": {"full": "We-imperative-null clause", "abbr": "WIm0"},
    "WImX": {"full": "We-imperative-X clause", "abbr": "WImX"},
    "WQt0": {"full": "We-qatal-null clause", "abbr": "WQt0"},
    "WQtX": {"full": "We-qatal-X clause", "abbr": "WQtX"},
    "WxI0": {"full": "We-x-imperative-null clause", "abbr": "WxI0"},
    "WXIm": {"full": "We-X-imperative clause", "abbr": "WXIm"},
    "WxIX": {"full": "We-x-imperative-X clause", "abbr": "WxIX"},
    "WxQ0": {"full": "We-x-qatal-null clause", "abbr": "WxQ0"},
    "WXQt": {"full": "We-X-qatal clause", "abbr": "WXQt"},
    "WxQX": {"full": "We-x-qatal-X clause", "abbr": "WxQX"},
    "WxY0": {"full": "We-x-yiqtol-null clause", "abbr": "WxY0"},
    "WXYq": {"full": "We-X-yiqtol clause", "abbr": "WXYq"},
    "WxYX": {"full": "We-x-yiqtol-X clause", "abbr": "WxYX"},
    "WYq0": {"full": "We-yiqtol-null clause", "abbr": "WYq0"},
    "WYqX": {"full": "We-yiqtol-X clause", "abbr": "WYqX"},
    "xIm0": {"full": "x-imperative-null clause", "abbr": "xIm0"},
    "XImp": {"full": "X-imperative clause", "abbr": "XImp"},
    "xImX": {"full": "x-imperative-X clause", "abbr": "xImX"},
    "XPos": {"full": "Extraposition", "abbr": "XPos"},
    "xQt0": {"full": "x-qatal-null clause", "abbr": "xQt0"},
    "XQtl": {"full": "X-qatal clause", "abbr": "XQtl"},
    "xQtX": {"full": "x-qatal-X clause", "abbr": "xQtX"},
    "xYq0": {"full": "x-yiqtol-null clause", "abbr": "xYq0"},
    "XYqt": {"full": "X-yiqtol clause", "abbr": "XYqt"},
    "xYqX": {"full": "x-yiqtol-X clause", "abbr": "xYqX"},
    "ZIm0": {"full": "Zero-imperative-null clause", "abbr": "ZIm0"},
    "ZImX": {"full": "Zero-imperative-X clause", "abbr": "ZImX"},
    "ZQt0": {"full": "Zero-qatal-null clause", "abbr": "ZQt0"},
    "ZQtX": {"full": "Zero-qatal-X clause", "abbr": "ZQtX"},
    "ZYq0": {"full": "Zero-yiqtol-null clause", "abbr": "ZYq0"},
    "ZYqX": {"full": "Zero-yiqtol-X clause", "abbr": "ZYqX"},
}

def eng_to_kor(term, option):
    if term == "unknown":
        return ''
    elif term in translate.keys():
        return translate[term][option]
    else:
        return term

def word_function(node):
    w_f = OrderedDict()
    w_f["원형"] = F.voc_utf8.v(L.u(node, otype='lex')[0])
    #w_f["어근"] = F.lex_utf8.v(node).replace('=', '').replace('/', '').replace('[', '')
    w_f["음역"] = F.phono.v(node)
    w_f["품사"] = F.sp.v(node)  # part of speech (verb, subs ..)
    w_f["시제"] = F.vt.v(node)  # vt = verbal tense
    w_f["동사형"] = F.vs.v(node)  # vs = verbal stem
    w_f["인칭"] = F.ps.v(node)  # person (p1, p2, p3)
    w_f["성"] = F.gn.v(node)  # gender
    w_f["수"] = F.nu.v(node)  # number (sg, pl, du)
    w_f["어형"] = F.st.v(node)  # construct/absolute/emphatic
    # w_f["접미어유무"] = "Yes" if F.g_prs_utf8.v(node) != "" else "No"
    w_f["인칭접미어"] = F.g_prs_utf8.v(node)  # pronominal suffix in Heb
    w_f["부가접미어"] = F.g_uvf_utf8.v(node)  # univalent final in Heb
    w_f["인칭(접미)"] = F.prs_ps.v(node)  # pronominal suffix person
    w_f["성(접미)"] = F.prs_gn.v(node)  # pronominal suffix gender
    w_f["수(접미)"] = F.prs_nu.v(node)  # pronominal suffix number
    w_f["의미"] = F.gloss.v(L.u(node, otype='lex')[0])
    return w_f

@app.route('/')
def main_page():
    return render_template('main.html')

@app.route('/developer/')
def developer_page():
    return render_template('developer.html')

@app.route('/license/')
def license_page():
    return render_template('license.html')

@app.route('/text/')
@app.route('/text/<book>')
@app.route('/text/<book>/<int:chapter>')
def text_page(book='Genesis', chapter=1):
    chpNode = T.nodeFromSection((book, chapter))
    verseNode = L.d(chpNode, otype='verse')
    whole_chpNode = T.nodeFromSection((book,))
    last_chp = T.sectionFromNode(whole_chpNode, lastSlot=True)
    verse = ""
    for v in verseNode:
        verse += '<span class=verse_num verse_node='+str(v)+'>'
        verse += str(T.sectionFromNode(v)[2])
        verse += ' </span>'
        wordsNode = L.d(v, otype='word')
        for w in wordsNode:
            verse += '<a tabindex=0 class=word_elm data-poload=/api/word/'+str(w)+' data-toggle=popover data-trigger=focus>'
            verse += F.g_word_utf8.v(w)
            verse += '</a>'
            if F.trailer_utf8.v(w):
                verse += '<span class=trailer>'
                verse += F.trailer_utf8.v(w)
                verse += '</span>'
    return render_template('text.html', verse=verse, book=book, chapter=chapter, last_chp=last_chp[1])


@app.route('/api/word/<int:node>')
def show_word_function(node):
    w_f = word_function(node)
    for k, v in w_f.items():
        w_f[k] = eng_to_kor(v, 'full')
    return render_template('word_api.html', w_f=w_f)

@app.route('/api/verse/<int:node>')
def show_verse_function(node):
    wordsNode = L.d(node, otype='word')
    wordsNode.reverse()
    verse_api = {'words': [], 'gloss': [], 'sp': [], 'parse': [], 'suff': []}
    for w in wordsNode:
        verse_api['words'].append(F.g_word_utf8.v(w))
        verse_api['gloss'].append(F.gloss.v(L.u(w, otype='lex')[0]))
        sp = eng_to_kor(F.sp.v(w), 'abbr')
        if sp == '동':
            sp_str = sp + "(" + eng_to_kor(F.vs.v(w), 'abbr') + ")"
            verse_api['sp'].append(sp_str)
            parse_str = eng_to_kor(F.vt.v(w), 'abbr') + "." + eng_to_kor(F.ps.v(w), 'abbr') + eng_to_kor(F.gn.v(w), 'abbr') + eng_to_kor(F.nu.v(w), 'abbr')
            verse_api['parse'].append(parse_str)
        elif sp == '명':
            verse_api['sp'].append(sp)
            parse_str = eng_to_kor(F.gn.v(w), 'abbr') + eng_to_kor(F.nu.v(w), 'abbr')
            verse_api['parse'].append(parse_str)
        else:
            verse_api['sp'].append(sp)
            verse_api['parse'].append('')
        if F.g_prs_utf8.v(w) != "":
            suff_str = "접미." + eng_to_kor(F.prs_ps.v(w), 'abbr') + eng_to_kor(F.prs_gn.v(w), 'abbr') + eng_to_kor(F.prs_nu.v(w), 'abbr')
            verse_api['suff'].append(suff_str)
        else:
            verse_api['suff'].append('')
    section = T.sectionFromNode(wordsNode[0])
    eng_chp_vrs = heb_vrs_to_eng(section[0], str(section[1]), str(section[2]))
    verse_str = {"kjv": [], "kor": []}
    for c_v in eng_chp_vrs:
        chp_vrs = re.split(":", c_v)
        verse_str['kjv'].append(json_to_verse(section[0], chp_vrs[0], chp_vrs[1], 'kjv'))
        verse_str['kor'].append(json_to_verse(section[0], chp_vrs[0], chp_vrs[1], 'korean'))

    return render_template('verse_api.html', verse_api=verse_api, section=section, verse_str=verse_str)
