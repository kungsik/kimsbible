import os
import json
import codecs
from flask import request


#외부 API를 이용한 번역본 인용.
'''
def json_to_verse(book, chp, verse, ver):
    url = "https://getbible.net/json?passage=" + book + "_" + chp + ":" + verse + "&version=" + ver
    with urllib.request.urlopen(url) as u:
        data = u.read().decode().replace('(', '').replace(');', '')
        verse_json = json.loads(data)
        try:
            verse_str = chp + ":" + verse + " " + verse_json['book'][0]['chapter'][verse]['verse']
            return verse_str
        except KeyError:
            return 'DB 오류로 번역지원되지 않음'
'''
#자체 json 파일로 번역본 인용
def json_to_verse(book, chp, verse, ver):
    path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
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
        try:
            verse_str = chp + ":" + verse + " " + d[book_code[book]]['chapters'][json_chp][chp][verse]
            return verse_str
        except KeyError:
            return 'DB 오류로 번역지원되지 않음.'

def heb_vrs_to_eng(book, chp, verse):
    vrs_str = chp + ":" + verse
    path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
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
    "VC": {"full": "동사절(큰단위)", "abbr": "동절(큰)"},
    "NC": {"full": "명사절(큰단위)", "abbr": "명절(큰)"},
    "WC": {"full": "불완전절", "abbr": "불절"},
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
    "VP": {"full": "동사구", "abbr": "동"},
    "NP": {"full": "명사구", "abbr": "명"},
    "PrNP": {"full": "고유명사구", "abbr": "고명"},
    "AdvP": {"full": "부사구", "abbr": "고명"},
    "PP": {"full": "전치사구", "abbr": "전"},
    "CP": {"full": "접속구", "abbr": "접"},
    "PPrP": {"full": "대명사구", "abbr": "대명"},
    "DPrP": {"full": "지시대명사구", "abbr": "지대"},
    "IPrP": {"full": "의문대명사구", "abbr": "의대"},
    "InjP": {"full": "감탄사구", "abbr": "감탄"},
    "NegP": {"full": "부정(否定)사구", "abbr": "부정사"},
    "InrP": {"full": "의문사구", "abbr": "의문"},
    "AdjP": {"full": "형용사구", "abbr": "형"},
    "Adju": {"full": "부가어", "abbr": "부가"},
    "Cmpl": {"full": "보어",  "abbr": "보"},
    "Conj": {"full": "접속어", "abbr": "접"},
    "EPPr": {"full": "전접인칭대명사", "abbr": "전인대"},
    "ExsS": {"full": "주격접미어가 있는 존재어", "abbr": "주접존"},
    "Exst": {"full": "존재어", "abbr": "존재"},
    "Frnt": {"full": "전방도치어", "abbr": "전도치"},
    "Intj": {"full": "감탄사", "abbr": "감탄"},
    "IntS": {"full": "주격접미어가 있는 감탄사", "abbr": "주접감탄"},
    "Loca": {"full": "장소격", "abbr": "장소"},
    "Modi": {"full": "수식어", "abbr": "수식"},
    "ModS": {"full": "주격접미어가 있는 수식어", "abbr": "주접수식"},
    "NCop": {"full": "비존재어", "abbr": "비존"},
    "NCoS": {"full": "주격접미어가 있는 비존재어", "abbr": "주접비존"},
    "Nega": {"full": "부정어", "abbr": "부정"},
    "Objc": {"full": "목적어", "abbr": "목"},
    "PrAd": {"full": "서술격 부가어", "abbr": "술부"},
    "PrcS": {"full": "주격접미어가 있는 서술격 보어", "abbr": "주접술보"},
    "PreC": {"full": "서술격 보어", "abbr": "술보"},
    "Pred": {"full": "서술어", "abbr": "술"},
    "PreO": {"full": "목적격 접미어가 있는 서술어", "abbr": "목접술"},
    "PreS": {"full": "주격 접미어가 있는 서술어", "abbr": "주접술"},
    "PtcO": {"full": "목적격 접미어가 있는 분사", "abbr": "목분"},
    "Ques": {"full": "질문", "abbr": "질"},
    "Rela": {"full": "관계사", "abbr": "관계"},
    "Subj": {"full": "주어", "abbr": "주"},
    "Supp": {"full": "보충어", "abbr": "보충"},
    "Time": {"full": "시간표시", "abbr": "시간"}
}

def eng_to_kor(term, option):
    if term == "unknown":
        return ''
    elif term in translate.keys():
        return translate[term][option]
    else:
        return term
