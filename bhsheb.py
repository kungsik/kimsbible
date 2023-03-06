import re
import os
import csv
from collections import OrderedDict
from io import StringIO

from flask import render_template, request, url_for
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
TF = Fabric(locations='text-fabric-data', modules=ETCBC)
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
    w_f["사전1"] = "<a href='https://dict.naver.com/hbokodict/ancienthebrew/#/search?query=" + strong + "' target=_blank>네이버사전</a>"
    w_f["사전2"] = "<a href='https://biblehub.com/hebrew/" + strong + ".htm' target=_blank>바이블허브</a>"
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
        last_chp = T.sectionFromNode(whole_chpNode, lastSlot=True)
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

            #절분석 버튼
            verse +=  '<br><span>'
            verse += '<button type="button" class="btn btn-outline-secondary btn-sm bhsheb_verse_analysis" verse_node='+str(v)+'>절분석</button>'
            verse += '</span> '

            #절노트 버튼
            versenote_url = "../../commentary/vcode/" + vcode + "/"
            verse += '<span>'
            verse += '<a href="' + versenote_url + '" target="_blank"><button class="btn btn-outline-secondary btn-sm verse_note">주석</button></a>'
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

        #캐싱페이지 작성
        data = render_template('bhsheb_text.html', verse=verse, book=book, chapter=chapter, last_chp=last_chp[1], kml_file=kml_file, google_map_api=google_map_api, vcode=str(vcode))
        f = open("kimsbible/static/cached/bhsheb/" + book + "-" + str(chapter) + ".html", 'w')
        f.write(data)
        f.close()

        return render_template('bhsheb_text.html', verse=verse, book=book, chapter=chapter, last_chp=last_chp[1], kml_file=kml_file, google_map_api=google_map_api, vcode=str(vcode))
    
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
    wordsNode = L.d(node, otype='word')
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
