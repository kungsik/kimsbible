import re
import os
import csv
import sqlite3
import xml.etree.ElementTree as ET
from collections import OrderedDict, defaultdict
from io import StringIO

import requests as req
from flask import render_template, request, url_for, jsonify
from tf.fabric import Fabric

from kimsbible import app
from kimsbible.lib import lib as kb
from kimsbible.lib import vcodeparser as vp
from kimsbible.lib import db

from kimsbible.lib.config import google_map_api, kml_url

# @app.after_request
# def set_response_headers(r):
#     r.headers['Cache-Control'] = 'public, max-age=3600'
#     return r

### Load up TF ###
ETCBC = 'hebrew/etcbc4c'
TF = Fabric(locations=os.path.expanduser('~/text-fabric-data'), modules=ETCBC)
#api = TF.load('book')

api = TF.load('''
    book chapter verse
    nu gn ps vt vs st
    otype typ function
    det pdp qere_utf8 qere_trailer_utf8
    g_word_utf8 trailer_utf8
    lex_utf8 lex voc_utf8
    g_prs_utf8 g_uvf_utf8
    prs_gn prs_nu prs_ps g_cons_utf8
    gloss phono 
''')

api.makeAvailableIn(globals())

# ── 평행구 데이터 (ParallelPassages.xml) ─────────────────────────────────────
# XML 책 약어 → TF 책 이름 (구약)
_XML_TO_TF_HEB = {
    'GEN':'Genesis','EXO':'Exodus','LEV':'Leviticus','NUM':'Numbers','DEU':'Deuteronomy',
    'JOS':'Joshua','JDG':'Judges','1SA':'1_Samuel','2SA':'2_Samuel',
    '1KI':'1_Kings','2KI':'2_Kings','1CH':'1_Chronicles','2CH':'2_Chronicles',
    'EZR':'Ezra','NEH':'Nehemiah','EST':'Esther','JOB':'Job','PSA':'Psalms',
    'PRO':'Proverbs','ECC':'Ecclesiastes','SNG':'Song_of_songs',
    'ISA':'Isaiah','JER':'Jeremiah','LAM':'Lamentations','EZK':'Ezekiel',
    'DAN':'Daniel','HOS':'Hosea','JOL':'Joel','AMO':'Amos','OBA':'Obadiah',
    'JON':'Jonah','MIC':'Micah','NAM':'Nahum','HAB':'Habakkuk','ZEP':'Zephaniah',
    'HAG':'Haggai','ZEC':'Zechariah','MAL':'Malachi',
}
# XML 책 약어 → sblgnt URL 책 이름 (신약)
_XML_TO_TF_GRK = {
    'MAT':'Matthew','MRK':'Mark','LUK':'Luke','JHN':'John','ACT':'Acts',
    'ROM':'Romans','1CO':'1_Corinthians','2CO':'2_Corinthians','GAL':'Galatians',
    'EPH':'Ephesians','PHP':'Philippians','COL':'Colossians',
    '1TH':'1_Thessalonians','2TH':'2_Thessalonians','1TI':'1_Timothy','2TI':'2_Timothy',
    'TIT':'Titus','PHM':'Philemon','HEB':'Hebrews','JAS':'James',
    '1PE':'1_Peter','2PE':'2_Peter','1JN':'1_John','2JN':'2_John','3JN':'3_John',
    'JUD':'Jude','REV':'Revelation',
}
# TF 구약 책 이름 → XML 약어 (역방향)
_TF_TO_XML_HEB = {v: k for k, v in _XML_TO_TF_HEB.items()}

# ── 평행구 한글 책 이름 ─────────────────────────────────────────────────────────
_PARALLEL_KOR_NAME = {
    # 구약
    'GEN':'창세기','EXO':'출애굽기','LEV':'레위기','NUM':'민수기','DEU':'신명기',
    'JOS':'여호수아','JDG':'사사기','RUT':'룻기','1SA':'사무엘상','2SA':'사무엘하',
    '1KI':'열왕기상','2KI':'열왕기하','1CH':'역대상','2CH':'역대하',
    'EZR':'에스라','NEH':'느헤미야','EST':'에스더','JOB':'욥기','PSA':'시편',
    'PRO':'잠언','ECC':'전도서','SNG':'아가','ISA':'이사야','JER':'예레미야',
    'LAM':'예레미야애가','EZK':'에스겔','DAN':'다니엘','HOS':'호세아','JOL':'요엘',
    'AMO':'아모스','OBA':'오바댜','JON':'요나','MIC':'미가','NAM':'나훔',
    'HAB':'하박국','ZEP':'스바냐','HAG':'학개','ZEC':'스가랴','MAL':'말라기',
    # 신약
    'MAT':'마태복음','MRK':'마가복음','LUK':'누가복음','JHN':'요한복음',
    'ACT':'사도행전','ROM':'로마서','1CO':'고린도전서','2CO':'고린도후서',
    'GAL':'갈라디아서','EPH':'에베소서','PHP':'빌립보서','COL':'골로새서',
    '1TH':'데살로니가전서','2TH':'데살로니가후서','1TI':'디모데전서','2TI':'디모데후서',
    'TIT':'디도서','PHM':'빌레몬서','HEB':'히브리서','JAS':'야고보서',
    '1PE':'베드로전서','2PE':'베드로후서','1JN':'요한일서','2JN':'요한이서',
    '3JN':'요한삼서','JUD':'유다서','REV':'요한계시록',
}

# 평행구 번역 조회용 책 인덱스 (JSON 배열 순서)
_PARALLEL_OT_IDX = {
    'GEN':0,'EXO':1,'LEV':2,'NUM':3,'DEU':4,'JOS':5,'JDG':6,'RUT':7,
    '1SA':8,'2SA':9,'1KI':10,'2KI':11,'1CH':12,'2CH':13,'EZR':14,'NEH':15,
    'EST':16,'JOB':17,'PSA':18,'PRO':19,'ECC':20,'SNG':21,'ISA':22,'JER':23,
    'LAM':24,'EZK':25,'DAN':26,'HOS':27,'JOL':28,'AMO':29,'OBA':30,'JON':31,
    'MIC':32,'NAM':33,'HAB':34,'ZEP':35,'HAG':36,'ZEC':37,'MAL':38,
}
_PARALLEL_NT_IDX = {
    'MAT':0,'MRK':1,'LUK':2,'JHN':3,'ACT':4,'ROM':5,'1CO':6,'2CO':7,
    'GAL':8,'EPH':9,'PHP':10,'COL':11,'1TH':12,'2TH':13,'1TI':14,'2TI':15,
    'TIT':16,'PHM':17,'HEB':18,'JAS':19,'1PE':20,'2PE':21,'1JN':22,'2JN':23,
    '3JN':24,'JUD':25,'REV':26,
}

# 개역한글 번역 JSON 로드 (모듈 시작 시 1회)
import json as _json_mod
_KOR_OT = []
_KOR_NT = []
_kor_ot_path = os.path.join(app.root_path, 'static', 'json', 'korean.json')
_kor_nt_path = os.path.join(app.root_path, 'static', 'json', 'kor_new.json')
if os.path.exists(_kor_ot_path):
    with open(_kor_ot_path, 'r', encoding='utf-8') as _f:
        _KOR_OT = _json_mod.load(_f)
if os.path.exists(_kor_nt_path):
    with open(_kor_nt_path, 'r', encoding='utf-8') as _f:
        _KOR_NT = _json_mod.load(_f)

def _get_parallel_verse_text(book_code, chapter, verse):
    """XML 책 약어 + 장 + 절 → 개역한글 번역 텍스트"""
    try:
        if book_code in _PARALLEL_OT_IDX:
            idx = _PARALLEL_OT_IDX[book_code]
            return _KOR_OT[idx]['chapters'][chapter - 1][str(chapter)][str(verse)]
        elif book_code in _PARALLEL_NT_IDX:
            idx = _PARALLEL_NT_IDX[book_code]
            return _KOR_NT[idx]['chapters'][chapter - 1][str(chapter)][str(verse)]
    except (IndexError, KeyError, TypeError):
        pass
    return ''

# 평행구 룩업: {"GEN 1:27": [{"ref":"GEN 5:2","type":"HEB"}, ...], ...}
_PARALLEL = defaultdict(list)
_parallel_xml = os.path.join(app.root_path, 'static', 'json', 'ParallelPassages.xml')
if os.path.exists(_parallel_xml):
    _pt = ET.parse(_parallel_xml)
    for _passage in _pt.getroot().findall('Passage'):
        _verses = _passage.findall('Verse')
        _refs = [(v.text.strip(), 'HEB' if v.get('HEB') else 'GRK') for v in _verses]
        for i, (_ref, _type) in enumerate(_refs):
            _others = [{'ref': r, 'type': t} for j, (r, t) in enumerate(_refs) if j != i]
            _PARALLEL[_ref].extend(_others)

def _tf_to_xml_ref(tf_book, chapter, verse):
    """TF 책 이름 + 장 + 절 → XML 참조 문자열 (예: 'GEN 1:27')"""
    abbr = _TF_TO_XML_HEB.get(tf_book)
    if not abbr:
        return None
    return f'{abbr} {chapter}:{verse}'

def _xml_ref_to_url(ref, ref_type):
    """XML 참조 (예: 'GEN 1:27') → 앱 내부 URL"""
    parts = ref.split()
    if len(parts) != 2:
        return None, None, None
    abbr = parts[0]
    cv = parts[1].split(':')
    chp = cv[0]
    vrs = cv[1].split('-')[0]  # 범위 구절은 시작 절만
    if ref_type == 'HEB':
        book = _XML_TO_TF_HEB.get(abbr)
        if book:
            return f'/bhsheb/{book}/{chp}', book, chp
    else:
        book = _XML_TO_TF_GRK.get(abbr)
        if book:
            return f'/sblgnt/{book}/{chp}', book, chp
    return None, None, None

# ── UBS SDBH 히브리어 사전 — DB 경로 및 도메인 맵 (SDBH 팝업 엔드포인트에서 사용)
_heb_db = os.path.join(app.root_path, 'static', 'json', 'heb_dict.db')

# 의미 영역(Lexical Domains) 코드 → 라벨 매핑 (112KB JSON, 직접 로드)
_HEB_DOMAINS = {}
_heb_domain_json = os.path.join(app.root_path, 'static', 'json',
                                 'UBSHebrewDicLexicalDomains-v0.9.2-en.JSON')
if os.path.exists(_heb_domain_json):
    import json as _json
    with open(_heb_domain_json, 'r', encoding='utf-8') as _f:
        for _d in _json.load(_f):
            _locs = _d.get('SemanticDomainLocalizations') or []
            _HEB_DOMAINS[_d['Code']] = _locs[0]['Label'] if _locs else ''

# TF 책 이름 → Sefaria API 책 이름 매핑
SEFARIA_BOOK_MAP = {
    "Genesis": "Genesis", "Exodus": "Exodus", "Leviticus": "Leviticus",
    "Numbers": "Numbers", "Deuteronomy": "Deuteronomy",
    "Joshua": "Joshua", "Judges": "Judges", "Ruth": "Ruth",
    "1_Samuel": "I_Samuel", "2_Samuel": "II_Samuel",
    "1_Kings": "I_Kings", "2_Kings": "II_Kings",
    "Isaiah": "Isaiah", "Jeremiah": "Jeremiah", "Ezekiel": "Ezekiel",
    "Hosea": "Hosea", "Joel": "Joel", "Amos": "Amos",
    "Obadiah": "Obadiah", "Jonah": "Jonah", "Micah": "Micah",
    "Nahum": "Nahum", "Habakkuk": "Habakkuk", "Zephaniah": "Zephaniah",
    "Haggai": "Haggai", "Zechariah": "Zechariah", "Malachi": "Malachi",
    "Psalms": "Psalms", "Job": "Job", "Proverbs": "Proverbs",
    "Song_of_songs": "Song_of_Songs", "Ruth": "Ruth",
    "Lamentations": "Lamentations", "Ecclesiastes": "Ecclesiastes",
    "Esther": "Esther", "Daniel": "Daniel", "Ezra": "Ezra",
    "Nehemiah": "Nehemiah",
    "1_Chronicles": "I_Chronicles", "2_Chronicles": "II_Chronicles",
}

# 대한성서공회 URL 코드 매핑 (구약)
_BSKOREA_HEB_MAP = {
    'Genesis': 'GEN', 'Exodus': 'EXO', 'Leviticus': 'LEV',
    'Numbers': 'NUM', 'Deuteronomy': 'DEU', 'Joshua': 'JOS',
    'Judges': 'JDG', 'Ruth': 'RUT', '1_Samuel': '1SA',
    '2_Samuel': '2SA', '1_Kings': '1KI', '2_Kings': '2KI',
    '1_Chronicles': '1CH', '2_Chronicles': '2CH', 'Ezra': 'EZR',
    'Nehemiah': 'NEH', 'Esther': 'EST', 'Job': 'JOB',
    'Psalms': 'PSA', 'Proverbs': 'PRO', 'Ecclesiastes': 'ECC',
    'Song_of_songs': 'SNG', 'Isaiah': 'ISA', 'Jeremiah': 'JER',
    'Lamentations': 'LAM', 'Ezekiel': 'EZK', 'Daniel': 'DAN',
    'Hosea': 'HOS', 'Joel': 'JOL', 'Amos': 'AMO',
    'Obadiah': 'OBA', 'Jonah': 'JON', 'Micah': 'MIC',
    'Nahum': 'NAM', 'Habakkuk': 'HAB', 'Zephaniah': 'ZEP',
    'Haggai': 'HAG', 'Zechariah': 'ZEC', 'Malachi': 'MAL',
}

# kml 파일 관련
book_abb = {
    "Genesis": "gen",
    "Exodus": "exod",
    "Leviticus": "lev",
    "Numbers": "num",
    "Deuteronomy": "deut",
    "Joshua": "josh",
    "Judges": "judg",
    "1_Samuel": "1sam",
    "2_Samuel": "2sam",
    "1_Kings": "1kgs",
    "2_Kings": "2kgs",
    "Isaiah": "isa",
    "Jeremiah": "jer",
    "Ezekiel": "ezek",
    "Hosea": "hos",
    "Joel": "joel",
    "Amos": "amos",
    "Obadiah": "obad",
    "Jonah": "jonah",
    "Micah": "mic",
    "Nahum": "nah",
    "Habakkuk": "hab",
    "Zephaniah": "zeph",
    "Haggai": "hag",
    "Zechariah": "zech",
    "Malachi": "mal",
    "Psalms": "ps",
    "Job": "job",
    "Proverbs": "none",
    "Ruth": "ruth",
    "Song_of_songs": "song",
    "Ecclesiastes": "eccl",
    "Lamentations": "lam",
    "Esther": "esth",
    "Daniel": "dan",
    "Ezra": "ezra",
    "Nehemiah": "neh",
    "1_Chronicles": "1chr",
    "2_Chronicles": "2chr"
}

def show_bhsheb_word_function(node):
    w_f = OrderedDict()
    w_f["원형"] = F.voc_utf8.v(L.u(node, otype='lex')[0])
    #w_f["어근"] = F.lex_utf8.v(node).replace('=', '').replace('/', '').replace('[', '')
    w_f["음역"] = F.phono.v(node)
    w_f["품사"] = F.pdp.v(node)  # part of speech (verb, subs ..)
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
    # w_f["의미"] = F.gloss.v(L.u(node, otype='lex')[0])
    # w_f["의미"] = w_f["의미"].replace('<', '[').replace('>', ']')
    strong = get_strong(node)
    w_f["의미"] = get_kor_hgloss(strong, node)
    w_f["사전1"] = "<a href='#' onclick=\"openDictPopup('https://dict.naver.com/hbokodict/ancienthebrew/#/search?query=" + strong + "'); return false;\">네이버사전</a>"
    w_f["사전2"] = "<a href='#' onclick=\"openDictPopup('https://biblehub.com/hebrew/" + strong + ".htm'); return false;\">바이블허브</a>"
    w_f["사전3"] = "<a href='#' onclick=\"openDictPopup('/bhsheb/sdbh/" + strong + "/'); return false;\">SDBH</a>"
    #w_f["사전"] = "<a href='http://dict.naver.com/hbokodict/ancienthebrew/#/search?query=" + w_f["원형"] + "' target=_blank>보기</a>"
    w_f["용례"] = "<a href='/bhsheb/search/?cons=" + F.lex_utf8.v(node) + "&sp=" + w_f["품사"] + "' target=_blank>검색</a>"

    if w_f["동사형"] != "NA" and w_f["동사형"] != "" and w_f["동사형"] != "unknown":
        w_f["동사형태"] = "<a href='/bhsheb/conjugator/?cons=" + w_f["원형"] + "' target=_blank>검색</a>"
        w_f["변화형"] = "<a href='https://www.pealim.com/search/?q=" + w_f["원형"] +  "' target=_blank>검색</a>"

    return w_f

def get_strong(node):
    if int(node) < 50001:
        csv_file = 'kimsbible/static/csv/strong1.csv'
        row_num = int(node) - 1
    elif int(node) < 100001:
        csv_file = 'kimsbible/static/csv/strong2.csv'
        row_num = int(node) - 50001
    elif int(node) < 150001:
        csv_file = 'kimsbible/static/csv/strong3.csv'
        row_num = int(node) - 100001
    elif int(node) < 200001:
        csv_file = 'kimsbible/static/csv/strong4.csv'
        row_num = int(node) - 150001
    elif int(node) < 250001:
        csv_file = 'kimsbible/static/csv/strong5.csv'
        row_num = int(node) - 200001
    elif int(node) < 300001:
        csv_file = 'kimsbible/static/csv/strong6.csv'
        row_num = int(node) - 250001
    elif int(node) < 350001:
        csv_file = 'kimsbible/static/csv/strong7.csv'
        row_num = int(node) - 300001
    elif int(node) < 400001:
        csv_file = 'kimsbible/static/csv/strong8.csv'
        row_num = int(node) - 350001
    else:
        csv_file = 'kimsbible/static/csv/strong9.csv' 
        row_num = int(node) - 400001

    f = open(csv_file, 'r', encoding='utf-8')
    strong = list(csv.reader(f))
    result = strong[row_num]
    f.close()
    return result[0]

def get_kor_hgloss(strongnum, w):
    if int(strongnum) > 4000:
        csv_file = 'kimsbible/static/csv/hstrong2.csv'
        row_num = int(strongnum) - 4001
    else: 
        csv_file = 'kimsbible/static/csv/hstrong1.csv'
        row_num = int(strongnum) - 1 
    
    f = open(csv_file, 'r', encoding='utf-8')
    hstrong = list(csv.reader(f))
    try:
        gloss = hstrong[row_num]
        f.close()
        result = gloss[1].split(';')
        return result[0]
    except:
        f.close()
        return F.gloss.v(L.u(w, otype='lex')[0]).replace('and', '그리고').replace('in', '~안에').replace('to', '~향해').replace('the', '[정관사]').replace('as', '~같이')


@app.route('/')
def main_page():
    commentary_db = db.Commentary()
    recent_posts_commentary = commentary_db.get_recent('commentary', 3)
    img_pattern = re.compile(r"<img[^>]*src=[\"']?([^>\"']+)[\"']?[^>]*>")
    
    title = []
    content = []
    img = []
    date = []
    author = []
    no = []
    urltitle = []

    for post in recent_posts_commentary:
        title.append(post[4])

        try:
            img.append(re.findall(img_pattern, str(post[5]))[0])
        except:
            img.append("https://app.alphalef.com/static/img/logo.png")

        date.append(post[1].split(' ')[0])
        author.append(post[2])

        content_text = re.sub('<.+?>', '', post[5], 0, re.I|re.S)
        content_text = re.sub('$.+?;', '', content_text, 0, re.I|re.S)
        content.append(content_text[0:150])

        no.append(post[0])
        urltitle.append(post[10])

    forum_db = db.Forum()
    recent_forum_topic = forum_db.get_recent_topic(3)

    # recent_posts_classic = commentary_db.get_recent('classic', 5)
    # return render_template('main.html', recent_posts_commentary=recent_posts_commentary, recent_posts_classic=recent_posts_classic)
    return render_template('main.html', author=author, date=date, img=img, content=content, title=title, urltitle=urltitle, no=no, recent_forum_topic=recent_forum_topic)


@app.route('/community/')
def community_page():
    return render_template('community.html')

@app.route('/bhsheb/')
@app.route('/text/')
@app.route('/bhsheb/<book>')
@app.route('/text/<book>')
@app.route('/bhsheb/<book>/<int:chapter>')
@app.route('/text/<book>/<int:chapter>')
def text_page(book='Genesis', chapter=1):
    #캐싱파일 유무 확인
    if not os.path.isfile("kimsbible/static/cached/bhsheb/" + book + "-" + str(chapter) + ".html"):

        chpNode = T.nodeFromSection((book, chapter))
        verseNode = L.d(chpNode, otype='verse')
        whole_chpNode = T.nodeFromSection((book,))
        chapter_nodes = L.d(whole_chpNode, otype='chapter')
        last_chp_num = T.sectionFromNode(chapter_nodes[-1])[1]
        verse = "<ol>"

        #성경읽기 도우미 코드에서 1절 번호를 구하기 위해 절수를 구함
        i = -1

        for v in verseNode:
            i = i + 1

            section = T.sectionFromNode(v)
            vcode = vp.nodetocode(section, vp.bookList)
            
            verse += '<li id='+str(i)+'>'
            verse += '<div class=verseContainer>'
            verse += '<div class=verseNode>'
            wordsNode = L.d(v, otype='word')
            for w in wordsNode:
                clauseNode = L.u(w, otype='clause')
                phraseNode = L.u(w, otype='phrase')
                firstClauseWordNode = L.d(clauseNode[0], otype='word')[0]
                firstPhraseWordNode = L.d(phraseNode[0], otype='word')[0]
                lastClauseWordNode = L.d(clauseNode[0], otype='word')[-1]
                lastPhraseWordNode = L.d(phraseNode[0], otype='word')[-1]

                if w == firstClauseWordNode:
                    verse += '<span class=clauseNode clause_node='+str(clauseNode[0])+'>'
                    verse += "<span class=clause1>C:"+ kb.eng_to_kor(F.typ.v(clauseNode[0]), 'full') +"</span>"

                if w == firstPhraseWordNode:
                    verse += '<span class=phraseNode phrase_node='+str(phraseNode[0])+'>'
                    verse += "<span class=phrase1>P:"+ kb.eng_to_kor(F.typ.v(phraseNode[0]), 'full') + "," + kb.eng_to_kor(F.function.v(phraseNode[0]), 'full') + "</span>"

                if F.qere_utf8.v(w):
                    verse += '<span class=wordNode>'
                    verse += F.g_word_utf8.v(w) + ' '
                    verse += '</a></span>'

                    verse += '<span class=wordNode><a tabindex=0 class=word_elm data-poload=/bhsheb/word/'+str(w)+' data-toggle=popover data-trigger=focus>'
                    verse += F.qere_utf8.v(w)
                    verse += '</a></span>'

                    if F.qere_trailer_utf8.v(w):
                        verse += '<span class=trailerNode>'
                        verse += F.qere_trailer_utf8.v(w)
                        verse += '</span>'

                else:
                    # 정관사와 전치사가 결합된 단어의 경우 빈 값으로 전치사 정보가 들어와서 틀이 깨지는 현상을 방지하기 위함.
                    if not F.g_word_utf8.v(w):
                        continue

                    verse += '<span class=wordNode><a tabindex=0 class=word_elm data-poload=/bhsheb/word/'+str(w)+' data-toggle=popover data-trigger=focus>'
                    verse += F.g_word_utf8.v(w)
                    verse += '</a></span>'

                    if F.trailer_utf8.v(w):
                        verse += '<span class=trailerNode>'
                        verse += F.trailer_utf8.v(w)
                        verse += '</span>'

                if w == lastPhraseWordNode: verse += '</span>'
                if w == lastClauseWordNode: verse += '</span>'

            verse += '<br>'

            # 대한성서공회 버튼
            _bskorea_code = _BSKOREA_HEB_MAP.get(section[0])
            if _bskorea_code:
                _bskorea_url = 'https://bible.bskorea.or.kr/bible/NKT,NKRV/' + _bskorea_code + '.' + str(section[1]) + '.' + str(section[2])
                verse += '<span>'
                verse += '<a href="' + _bskorea_url + '" target="_blank"><button class="btn btn-outline-dark btn-sm">성서공회</button></a>'
                verse += '</span> '

            #절분석 버튼
            verse += '<span>'
            verse += '<button type="button" class="btn btn-outline-secondary btn-sm bhsheb_verse_analysis" verse_node='+str(v)+'>절분석</button>'
            verse += '</span> '

            #절노트 버튼
            versenote_url = "../../commentary/vcode/" + vcode + "/"
            verse += '<span>'
            verse += '<a href="' + versenote_url + '" target="_blank"><button class="btn btn-outline-secondary btn-sm verse_note">주석</button></a>'
            verse += '</span> '

            # Sefaria 주석 버튼
            sefaria_book = SEFARIA_BOOK_MAP.get(section[0], section[0])
            sefaria_ref = sefaria_book + '.' + str(section[1]) + '.' + str(section[2])
            verse += '<span>'
            verse += '<button type="button" class="btn btn-outline-info btn-sm sefaria_btn" data-ref="' + sefaria_ref + '">Sefaria</button>'
            verse += '</span>'

            # 평행구 버튼 (평행구가 존재하는 절에만 표시)
            _xml_ref = _tf_to_xml_ref(section[0], section[1], section[2])
            if _xml_ref and _xml_ref in _PARALLEL:
                verse += ' <span>'
                verse += '<button type="button" class="btn btn-outline-success btn-sm parallel_btn" data-ref="' + _xml_ref + '">평행구</button>'
                verse += '</span>'

            verse += '</div>' #versenode

            verse += '<div class="transversions">'
            #개역한글 번역본
            eng_chp_vrs = kb.heb_vrs_to_eng(section[0], str(section[1]), str(section[2]))
            for c_v in eng_chp_vrs:
                chp_vrs = re.split(":", c_v)
                kor_vrs = kb.json_to_verse(section[0], chp_vrs[0], chp_vrs[1], 'korean')

            verse += "<p class='kor' id='kor' dir=ltr align=left>" + kor_vrs + "</p>"

            #kjv 번역본
            eng_chp_vrs = kb.heb_vrs_to_eng(section[0], str(section[1]), str(section[2]))
            for c_v in eng_chp_vrs:
                chp_vrs = re.split(":", c_v)
                kjv_vrs = kb.json_to_verse(section[0], chp_vrs[0], chp_vrs[1], 'kjv')

            verse += "<p class='kjv' id='kjv' dir=ltr align=left>" + kjv_vrs + "</p>"
            verse += "</div>" #transversions

            verse += '</div>' #versecontainer

            verse += '</li>'

        verse += '</ol>'
        kml_file = kml_url + book_abb[book] + '.' + str(chapter) + '.' + "kml"

        #원문읽기도우미를 위한 코드 (1절을 구함)
        vcode = int(vcode) - int(i)

        # 캐싱페이지 작성
        data = render_template('bhsheb_text.html', verse=verse, book=book, chapter=chapter, last_chp=last_chp_num, kml_file=kml_file, google_map_api=google_map_api, vcode=str(vcode))
        cache_path = "kimsbible/static/cached/bhsheb/" + book + "-" + str(chapter) + ".html"
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(data)
        except Exception:
            pass

        return data
    
    #캐싱파일이 있을 경우 
    else:        
        return app.send_static_file("cached/bhsheb/" + book + "-" + str(chapter) + ".html")


@app.route('/bhsheb/word/<int:node>')
def show_word_function(node):
    w_f = show_bhsheb_word_function(node)
    for k, v in w_f.items():
        w_f[k] = kb.eng_to_kor(v, 'full')
    return render_template('bhsheb_word.html', w_f=w_f)

@app.route('/bhsheb/verse/<int:node>')
def show_verse_function(node):
    wordsNode = list(L.d(node, otype='word'))
    wordsNode.reverse()
    verse_api = {'words': [], 'gloss': [], 'pdp': [], 'parse': [], 'suff': []}
    for w in wordsNode:
        verse_api['words'].append(F.g_word_utf8.v(w))
        strong = get_strong(w)
        verse_api['gloss'].append(get_kor_hgloss(strong, w))
        # verse_api['gloss'].append(F.gloss.v(L.u(w, otype='lex')[0]))
        pdp = kb.eng_to_kor(F.pdp.v(w), 'abbr')
        if pdp == '동':
            pdp_str = pdp + "(" + kb.eng_to_kor(F.vs.v(w), 'abbr') + ")"
            verse_api['pdp'].append(pdp_str)
            parse_str = kb.eng_to_kor(F.vt.v(w), 'abbr') + "." + kb.eng_to_kor(F.ps.v(w), 'abbr') + kb.eng_to_kor(F.gn.v(w), 'abbr') + kb.eng_to_kor(F.nu.v(w), 'abbr')
            verse_api['parse'].append(parse_str)
        elif pdp == '명':
            verse_api['pdp'].append(pdp)
            parse_str = kb.eng_to_kor(F.gn.v(w), 'abbr') + kb.eng_to_kor(F.nu.v(w), 'abbr')
            verse_api['parse'].append(parse_str)
        else:
            verse_api['pdp'].append(pdp)
            verse_api['parse'].append('')
        if F.g_prs_utf8.v(w) != "":
            suff_str = "접미." + kb.eng_to_kor(F.prs_ps.v(w), 'abbr') + kb.eng_to_kor(F.prs_gn.v(w), 'abbr') + kb.eng_to_kor(F.prs_nu.v(w), 'abbr')
            verse_api['suff'].append(suff_str)
        else:
            verse_api['suff'].append('')
    section = T.sectionFromNode(wordsNode[0])
    eng_chp_vrs = kb.heb_vrs_to_eng(section[0], str(section[1]), str(section[2]))
    verse_str = {"kjv": [], "kor": []}
    for c_v in eng_chp_vrs:
        chp_vrs = re.split(":", c_v)
        verse_str['kjv'].append(kb.json_to_verse(section[0], chp_vrs[0], chp_vrs[1], 'kjv'))
        verse_str['kor'].append(kb.json_to_verse(section[0], chp_vrs[0], chp_vrs[1], 'korean'))

    return render_template('bhsheb_verse.html', verse_api=verse_api, section=section, verse_str=verse_str)


@app.route('/bhsheb/parallel/<path:ref>/')
def parallel_passages(ref):
    """평행구 목록 반환 (JSON) — 중복 제거, 한글 이름 + 개역한글 번역 포함"""
    seen = set()
    result = []
    for item in _PARALLEL.get(ref, []):
        if item['ref'] in seen:
            continue
        seen.add(item['ref'])
        url, _, _ = _xml_ref_to_url(item['ref'], item['type'])

        # 한글 책 이름 + 장절 조합
        parts = item['ref'].split(' ')
        book_code = parts[0]
        chap_verse = parts[1] if len(parts) > 1 else ''
        kor_name = _PARALLEL_KOR_NAME.get(book_code, book_code)
        kor_ref = kor_name + ' ' + chap_verse

        # 개역한글 번역 조회
        verse_text = ''
        if chap_verse:
            cv = chap_verse.split(':')
            if len(cv) == 2:
                try:
                    chap = int(cv[0])
                    verse_num = int(cv[1].split('-')[0])  # 범위(7-8)는 첫 절만
                    verse_text = _get_parallel_verse_text(book_code, chap, verse_num)
                except (ValueError, TypeError):
                    pass

        result.append({
            'ref':      item['ref'],
            'kor_ref':  kor_ref,
            'type':     item['type'],
            'url':      url,
            'text':     verse_text,
        })
    return jsonify(result)


@app.route('/bhsheb/sdbh/<strong>/')
def sdbh_popup(strong):
    """UBS SDBH 히브리어 사전 풀 팝업 페이지 — SQLite 직접 조회"""
    import json as _json
    try:
        hkey = 'H' + str(int(strong)).zfill(4)
    except (ValueError, TypeError):
        hkey = strong
    row = None
    if os.path.exists(_heb_db):
        _conn = sqlite3.connect(_heb_db)
        row = _conn.execute(
            'SELECT lemma, pos, full_data FROM dict WHERE strong=?', (hkey,)
        ).fetchone()
        _conn.close()
    if not row or not row[2]:
        return render_template('sdbh_popup.html', found=False, strong=hkey,
                               lemma='', pos='', senses=[], dict_name='Hebrew')
    fd = _json.loads(row[2])
    for s in fd.get('senses', []):
        s['domains'] = [_HEB_DOMAINS.get(c, c) for c in s.get('domain_codes', []) if c]
    return render_template('sdbh_popup.html', found=True, strong=hkey,
                           lemma=fd['lemma'], pos=fd['pos'],
                           senses=fd['senses'], dict_name='Hebrew (SDBH)')


@app.route('/bhsheb/sefaria/<path:ref>/')
def sefaria_proxy(ref):
    """Sefaria API 프록시 — CORS 우회, JPS 번역 + 주석 데이터 반환"""
    import concurrent.futures

    def fetch_jps(r):
        jps_url = ('https://www.sefaria.org/api/v3/texts/' + r
                   + '?version=english%7CTHE%20JPS%20TANAKH%3A%20Gender-Sensitive%20Edition'
                   + '&return_format=text_only')
        resp = req.get(jps_url, timeout=10)
        d = resp.json()
        versions = d.get('versions', [])
        if versions and isinstance(versions, list):
            return versions[0].get('text', '')
        return ''

    def fetch_links(r):
        links_url = 'https://www.sefaria.org/api/links/' + r
        resp = req.get(links_url, timeout=10)
        return resp.json()

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            jps_fut   = ex.submit(fetch_jps, ref)
            links_fut = ex.submit(fetch_links, ref)
            jps_text  = jps_fut.result()
            links_data = links_fut.result()

        SHOW_CATEGORIES = {'Commentary', 'Targum', 'Midrash'}
        links = []
        for item in links_data:
            if item.get('category') not in SHOW_CATEGORIES:
                continue
            text = item.get('text', '')
            if isinstance(text, list):
                text = ' '.join(t for t in text if t)
            links.append({
                'source':   item.get('index_title', ''),
                'category': item.get('category', ''),
                'ref':      item.get('sourceRef', ''),
                'text':     text,
            })

        return jsonify({'jps': jps_text, 'links': links})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
