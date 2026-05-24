import os
import sqlite3
import json as _json
from flask import render_template, request
from kimsbible import app

# UBS 그리스어 도메인 맵 — 모듈 시작 시 한 번만 로드 (236KB)
_GRK_DOMAINS = {}
_grk_domain_json = os.path.join(app.root_path, 'static', 'json',
                                 'UBSGreekNTDicLexicalDomains-v1.0-en.JSON')
if os.path.exists(_grk_domain_json):
    with open(_grk_domain_json, 'r', encoding='utf-8') as _f:
        for _d in _json.load(_f):
            _locs = _d.get('SemanticDomainLocalizations') or []
            _GRK_DOMAINS[_d['Code']] = _locs[0]['Label'] if _locs else ''
from kimsbible.lib.config import sblgnt_url, google_map_api, kml_url
from kimsbible.lib.vcodeparser import bookList
import requests
from kimsbible.lib.config import sblgnt_url

# @app.after_request
# def set_response_headers(r):
#     r.headers['Cache-Control'] = 'public, max-age=3600'
#     return r

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
    #캐싱파일 유무 확인
    if not os.path.isfile("kimsbible/static/cached/sblgnt/" + book + "-" + str(chapter) + ".html"):
        kml_file = kml_url + book_abb[book] + '.' + str(chapter) + '.' + "kml"

        #성경읽기 도우미를 위한 코드값
        if chapter < 10:
            zero = '00'
        else:
            zero = '0'
        vcode = str(bookList.index(book)) + zero + str(chapter) + '001'

        API_url = sblgnt_url + '/text/gnt/' + book + '/' + str(chapter) + '/'
        response = requests.get(API_url)
        verse = response.json()['verse']
        last_chp = response.json()['lastchp']

        #캐싱페이지 작성
        # data = render_template('sblgnt_text.html', book=book, chapter=chapter, kml_file=kml_file, sblgnt_url=sblgnt_url, google_map_api=google_map_api, vcode=vcode, verse=verse, last_chp=last_chp)
        # f = open("kimsbible/static/cached/sblgnt/" + book + "-" + str(chapter) + ".html", 'w')
        # f.write(data)
        # f.close()

        return render_template('sblgnt_text.html', book=book, chapter=chapter, kml_file=kml_file, sblgnt_url=sblgnt_url, google_map_api=google_map_api, vcode=vcode, verse=verse, last_chp=last_chp)

    #캐싱파일이 있을 경우
    else:
        return app.send_static_file("cached/sblgnt/" + book + "-" + str(chapter) + ".html")


@app.route('/sblgnt/word/<int:node>')
def show_sblgnt_word_function(node):
    API_url = sblgnt_url + '/word/gnt/' + str(node)
    response = requests.get(API_url)
    w_f = response.json()['gntwordinfo']

    return render_template('sblgnt_word.html', w_f=w_f)

@app.route('/sblgnt/verse/<int:node>')
def show_sblgnt_verse_function(node):
    return render_template('sblgnt_verse.html', node=node, sblgnt_url=sblgnt_url)


@app.route('/sblgnt/sdbh/<strong>/')
def sblgnt_sdbh_popup(strong):
    """UBS 그리스어 사전 풀 팝업 페이지"""
    _grk_db = os.path.join(app.root_path, 'static', 'json', 'grk_dict.db')
    try:
        gkey = 'G' + str(int(strong)).zfill(4)
    except (ValueError, TypeError):
        gkey = strong

    grk_domains = _GRK_DOMAINS  # 모듈 레벨에서 이미 로드됨

    # DB 조회
    if not os.path.exists(_grk_db):
        return render_template('sdbh_popup.html', found=False, strong=gkey,
                               lemma='', pos='', senses=[], dict_name='Greek')
    conn = sqlite3.connect(_grk_db)
    # G0001a 형태도 매칭되도록 LIKE 조회
    row = conn.execute(
        'SELECT lemma, pos, full_data FROM dict WHERE strong=? OR strong LIKE ?',
        (gkey, gkey + '%')
    ).fetchone()
    conn.close()

    if not row or not row[2]:
        return render_template('sdbh_popup.html', found=False, strong=gkey,
                               lemma='', pos='', senses=[], dict_name='Greek')
    fd = _json.loads(row[2])
    for s in fd.get('senses', []):
        s['domains'] = [grk_domains.get(c, c) for c in s.get('domain_codes', []) if c]
    return render_template('sdbh_popup.html', found=True, strong=gkey,
                           lemma=fd['lemma'], pos=fd['pos'],
                           senses=fd['senses'], dict_name='Greek NT (UBS)')
