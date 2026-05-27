// verse_jump.js — 구절 앵커 스크롤 보정 + 구절 바로가기 네비게이션 (ver 2)
(function () {
  'use strict';

  // ─── 1. 앵커 스크롤 보정 ───────────────────────────────────────────────────
  // 고정 헤더 높이를 동적으로 계산해 앵커로 이동할 때 헤더 아래에 절이 위치하도록 보정한다.

  function getNavbarHeight() {
    var nav = document.querySelector('.site-navbar');
    return nav ? nav.getBoundingClientRect().height + 10 : 75;
  }

  function scrollToId(id) {
    // 1차: id 속성으로 직접 탐색 (bhsheb 및 ID가 부여된 sblgnt 캐시)
    var el = document.getElementById(String(id));

    // 2차 폴백: id 속성이 없는 sblgnt 구버전 캐시 → 절 순서(1-based)로 탐색
    if (!el) {
      var verseNum = parseInt(id, 10);
      if (!isNaN(verseNum) && verseNum > 0) {
        // sblgnt: #text ol,  bhsheb: #verse_heb ol
        var ol = document.querySelector('#text ol, #verse_heb ol');
        if (ol) {
          var items = ol.children; // 직계 <li> 목록
          el = items[verseNum - 1] || null; // 1-based → 0-based
        }
      }
    }

    if (!el) return;
    var top = el.getBoundingClientRect().top + window.pageYOffset - getNavbarHeight();
    window.scrollTo(0, Math.max(0, top));
  }

  // 페이지 로드 시 해시가 있으면 브라우저 기본 스크롤을 덮어씀
  window.addEventListener('load', function () {
    if (window.location.hash) {
      setTimeout(function () {
        scrollToId(window.location.hash.slice(1));
      }, 150);
    }
  });

  // SPA 없이도 같은 페이지 안에서 해시 변경 시 보정
  window.addEventListener('hashchange', function () {
    setTimeout(function () {
      scrollToId(window.location.hash.slice(1));
    }, 50);
  });

  // ─── 2. 구절 바로가기 네비게이션 ──────────────────────────────────────────
  // bhsheb / sblgnt / 메인(/) 페이지에서 동작

  var pathname  = window.location.pathname;
  var textType  = pathname.split('/')[1];
  var isMainPage = (pathname === '/' || pathname === '');
  if (!isMainPage && textType !== 'bhsheb' && textType !== 'sblgnt') return;

  // 한글 약어/전체명 → [영문 책이름, OT여부]
  // 긴 것을 먼저 두어야 짧은 것이 먼저 매칭되는 오류를 방지한다.
  var KO_MAP = [
    // ── OT 전체명 ──────────────────────────────────────────────────────────
    ['창세기',        'Genesis',        true],
    ['출애굽기',      'Exodus',         true],
    ['레위기',        'Leviticus',      true],
    ['민수기',        'Numbers',        true],
    ['신명기',        'Deuteronomy',    true],
    ['여호수아',      'Joshua',         true],
    ['사사기',        'Judges',         true],
    ['사무엘상',      '1_Samuel',       true],
    ['사무엘하',      '2_Samuel',       true],
    ['열왕기상',      '1_Kings',        true],
    ['열왕기하',      '2_Kings',        true],
    ['역대상',        '1_Chronicles',   true],
    ['역대하',        '2_Chronicles',   true],
    ['에스라',        'Ezra',           true],
    ['느헤미야',      'Nehemiah',       true],
    ['에스더',        'Esther',         true],
    ['욥기',          'Job',            true],
    ['시편',          'Psalms',         true],
    ['잠언',          'Proverbs',       true],
    ['전도서',        'Ecclesiastes',   true],
    ['아가',          'Song_of_songs',  true],
    ['이사야',        'Isaiah',         true],
    ['예레미야애가',  'Lamentations',   true],   // 예레미야보다 먼저
    ['예레미야',      'Jeremiah',       true],
    ['에스겔',        'Ezekiel',        true],
    ['다니엘',        'Daniel',         true],
    ['호세아',        'Hosea',          true],
    ['요엘',          'Joel',           true],
    ['아모스',        'Amos',           true],
    ['오바댜',        'Obadiah',        true],
    ['요나',          'Jonah',          true],
    ['미가',          'Micah',          true],
    ['나훔',          'Nahum',          true],
    ['하박국',        'Habakkuk',       true],
    ['스바냐',        'Zephaniah',      true],
    ['학개',          'Haggai',         true],
    ['스가랴',        'Zechariah',      true],
    ['말라기',        'Malachi',        true],
    ['룻기',          'Ruth',           true],
    // ── OT 단축 (다자 먼저) ────────────────────────────────────────────────
    ['삼상', '1_Samuel',      true],
    ['삼하', '2_Samuel',      true],
    ['왕상', '1_Kings',       true],
    ['왕하', '2_Kings',       true],
    ['대상', '1_Chronicles',  true],
    ['대하', '2_Chronicles',  true],
    ['창',   'Genesis',       true],
    ['출',   'Exodus',        true],
    ['레',   'Leviticus',     true],
    ['민',   'Numbers',       true],
    ['신',   'Deuteronomy',   true],
    ['수',   'Joshua',        true],
    ['삿',   'Judges',        true],
    ['룻',   'Ruth',          true],
    ['스',   'Ezra',          true],
    ['느',   'Nehemiah',      true],
    ['에',   'Esther',        true],
    ['욥',   'Job',           true],
    ['시',   'Psalms',        true],
    ['잠',   'Proverbs',      true],
    ['전',   'Ecclesiastes',  true],
    ['아',   'Song_of_songs', true],
    ['사',   'Isaiah',        true],
    ['애',   'Lamentations',  true],
    ['렘',   'Jeremiah',      true],
    ['겔',   'Ezekiel',       true],
    ['단',   'Daniel',        true],
    ['호',   'Hosea',         true],
    ['욜',   'Joel',          true],
    ['암',   'Amos',          true],
    ['옵',   'Obadiah',       true],
    ['욘',   'Jonah',         true],
    ['미',   'Micah',         true],
    ['나',   'Nahum',         true],
    ['합',   'Habakkuk',      true],
    ['습',   'Zephaniah',     true],
    ['학',   'Haggai',        true],
    ['슥',   'Zechariah',     true],
    ['말',   'Malachi',       true],
    // ── NT 전체명 ──────────────────────────────────────────────────────────
    ['마태복음',        'Matthew',          false],
    ['마가복음',        'Mark',             false],
    ['누가복음',        'Luke',             false],
    ['요한복음',        'John',             false],
    ['사도행전',        'Acts',             false],
    ['로마서',          'Romans',           false],
    ['고린도전서',      '1_Corinthians',    false],
    ['고린도후서',      '2_Corinthians',    false],
    ['갈라디아서',      'Galatians',        false],
    ['에베소서',        'Ephesians',        false],
    ['빌립보서',        'Philippians',      false],
    ['골로새서',        'Colossians',       false],
    ['데살로니가전서',  '1_Thessalonians',  false],
    ['데살로니가후서',  '2_Thessalonians',  false],
    ['디모데전서',      '1_Timothy',        false],
    ['디모데후서',      '2_Timothy',        false],
    ['디도서',          'Titus',            false],
    ['빌레몬서',        'Philemon',         false],
    ['히브리서',        'Hebrews',          false],
    ['야고보서',        'James',            false],
    ['베드로전서',      '1_Peter',          false],
    ['베드로후서',      '2_Peter',          false],
    ['요한1서',         '1_John',           false],
    ['요한2서',         '2_John',           false],
    ['요한3서',         '3_John',           false],
    ['유다서',          'Jude',             false],
    ['요한계시록',      'Revelation',       false],
    // ── NT 단축 (다자 먼저 — 요일/요이/요삼은 반드시 요 앞에) ──────────────
    ['고전',  '1_Corinthians',   false],
    ['고후',  '2_Corinthians',   false],
    ['살전',  '1_Thessalonians', false],
    ['살후',  '2_Thessalonians', false],
    ['딤전',  '1_Timothy',       false],
    ['딤후',  '2_Timothy',       false],
    ['벧전',  '1_Peter',         false],
    ['벧후',  '2_Peter',         false],
    ['요일',  '1_John',          false],
    ['요이',  '2_John',          false],
    ['요삼',  '3_John',          false],
    ['마',    'Matthew',         false],
    ['막',    'Mark',            false],
    ['눅',    'Luke',            false],
    ['요',    'John',            false],
    ['행',    'Acts',            false],
    ['롬',    'Romans',          false],
    ['갈',    'Galatians',       false],
    ['엡',    'Ephesians',       false],
    ['빌',    'Philippians',     false],
    ['골',    'Colossians',      false],
    ['딛',    'Titus',           false],
    ['몬',    'Philemon',        false],
    ['히',    'Hebrews',         false],
    ['약',    'James',           false],
    ['유',    'Jude',            false],
    ['계',    'Revelation',      false],
  ];

  // 영어 약어/전체명 → [영문 책이름, OT여부]  (소문자, 긴 것 먼저)
  var EN_MAP = [
    ['1 thessalonians', '1_Thessalonians', false],
    ['2 thessalonians', '2_Thessalonians', false],
    ['1 corinthians',   '1_Corinthians',   false],
    ['2 corinthians',   '2_Corinthians',   false],
    ['1 chronicles',    '1_Chronicles',    true],
    ['2 chronicles',    '2_Chronicles',    true],
    ['song of songs',   'Song_of_songs',   true],
    ['song of solomon', 'Song_of_songs',   true],
    ['lamentations',    'Lamentations',    true],
    ['ecclesiastes',    'Ecclesiastes',    true],
    ['1 samuel',        '1_Samuel',        true],
    ['2 samuel',        '2_Samuel',        true],
    ['1 kings',         '1_Kings',         true],
    ['2 kings',         '2_Kings',         true],
    ['1 peter',         '1_Peter',         false],
    ['2 peter',         '2_Peter',         false],
    ['1 timothy',       '1_Timothy',       false],
    ['2 timothy',       '2_Timothy',       false],
    ['1 john',          '1_John',          false],
    ['2 john',          '2_John',          false],
    ['3 john',          '3_John',          false],
    ['philippians',     'Philippians',     false],
    ['deuteronomy',     'Deuteronomy',     true],
    ['revelation',      'Revelation',      false],
    ['colossians',      'Colossians',      false],
    ['ephesians',       'Ephesians',       false],
    ['galatians',       'Galatians',       false],
    ['proverbs',        'Proverbs',        true],
    ['nehemiah',        'Nehemiah',        true],
    ['habakkuk',        'Habakkuk',        true],
    ['zephaniah',       'Zephaniah',       true],
    ['zechariah',       'Zechariah',       true],
    ['leviticus',       'Leviticus',       true],
    ['obadiah',         'Obadiah',         true],
    ['hebrews',         'Hebrews',         false],
    ['matthew',         'Matthew',         false],
    ['genesis',         'Genesis',         true],
    ['ezekiel',         'Ezekiel',         true],
    ['malachi',         'Malachi',         true],
    ['numbers',         'Numbers',         true],
    ['psalms',          'Psalms',          true],
    ['psalm',           'Psalms',          true],
    ['romans',          'Romans',          false],
    ['judges',          'Judges',          true],
    ['joshua',          'Joshua',          true],
    ['isaiah',          'Isaiah',          true],
    ['daniel',          'Daniel',          true],
    ['haggai',          'Haggai',          true],
    ['esther',          'Esther',          true],
    ['micah',           'Micah',           true],
    ['james',           'James',           false],
    ['hosea',           'Hosea',           true],
    ['jonah',           'Jonah',           true],
    ['nahum',           'Nahum',           true],
    ['ezra',            'Ezra',            true],
    ['acts',            'Acts',            false],
    ['amos',            'Amos',            true],
    ['joel',            'Joel',            true],
    ['jude',            'Jude',            false],
    ['luke',            'Luke',            false],
    ['mark',            'Mark',            false],
    ['john',            'John',            false],
    ['ruth',            'Ruth',            true],
    ['titus',           'Titus',           false],
    ['job',             'Job',             true],
    ['song',            'Song_of_songs',   true],
    // 약어
    ['gen',   'Genesis',         true],
    ['exod',  'Exodus',          true],
    ['exo',   'Exodus',          true],
    ['lev',   'Leviticus',       true],
    ['num',   'Numbers',         true],
    ['deut',  'Deuteronomy',     true],
    ['deu',   'Deuteronomy',     true],
    ['josh',  'Joshua',          true],
    ['jos',   'Joshua',          true],
    ['judg',  'Judges',          true],
    ['jdg',   'Judges',          true],
    ['psa',   'Psalms',          true],
    ['prov',  'Proverbs',        true],
    ['eccl',  'Ecclesiastes',    true],
    ['isa',   'Isaiah',          true],
    ['jer',   'Jeremiah',        true],
    ['lam',   'Lamentations',    true],
    ['ezek',  'Ezekiel',         true],
    ['dan',   'Daniel',          true],
    ['hos',   'Hosea',           true],
    ['obad',  'Obadiah',         true],
    ['nah',   'Nahum',           true],
    ['hab',   'Habakkuk',        true],
    ['zeph',  'Zephaniah',       true],
    ['hag',   'Haggai',          true],
    ['zech',  'Zechariah',       true],
    ['mal',   'Malachi',         true],
    ['matt',  'Matthew',         false],
    ['mat',   'Matthew',         false],
    ['rom',   'Romans',          false],
    ['gal',   'Galatians',       false],
    ['eph',   'Ephesians',       false],
    ['php',   'Philippians',     false],
    ['phil',  'Philippians',     false],
    ['col',   'Colossians',      false],
    ['heb',   'Hebrews',         false],
    ['jas',   'James',           false],
    ['rev',   'Revelation',      false],
    ['jer',   'Jeremiah',        true],
  ];

  // "1:10" / "1장10절" / "1장 10절" 형식 파싱 → {chapter, verse}
  // verse 생략 시 verse: null
  function parseChapterVerse(str) {
    str = str.trim();
    var m = str.match(/^(\d+)\s*[:장]\s*(\d+)/);
    if (m) return { chapter: +m[1], verse: +m[2] };
    var m2 = str.match(/^(\d+)/);
    if (m2) return { chapter: +m2[1], verse: null };
    return null;
  }

  function parseRef(raw) {
    var s = raw.trim();

    // 한글 약어 순서대로 시도
    for (var i = 0; i < KO_MAP.length; i++) {
      var abbr = KO_MAP[i][0], en = KO_MAP[i][1], ot = KO_MAP[i][2];
      if (s.startsWith(abbr)) {
        var rest = s.slice(abbr.length).trim();
        var cv = parseChapterVerse(rest);
        if (cv) return { en: en, ot: ot, chapter: cv.chapter, verse: cv.verse };
      }
    }

    // 영어 약어 순서대로 시도 (소문자 변환 후)
    var sl = s.toLowerCase();
    for (var j = 0; j < EN_MAP.length; j++) {
      var ea = EN_MAP[j][0], een = EN_MAP[j][1], eot = EN_MAP[j][2];
      if (sl.startsWith(ea)) {
        var rest2 = s.slice(ea.length).trim();
        var cv2 = parseChapterVerse(rest2);
        if (cv2) return { en: een, ot: eot, chapter: cv2.chapter, verse: cv2.verse };
      }
    }

    return null;
  }

  function navigateToVerse() {
    var val = document.getElementById('verse-jump-input').value;
    var ref = parseRef(val);
    if (!ref) {
      alert('구절 형식을 확인해 주세요.\n예) 창 1:1  /  마 3:16  /  Genesis 1:1');
      return;
    }
    var base = ref.ot ? '/bhsheb/' : '/sblgnt/';
    var url  = base + ref.en + '/' + ref.chapter;
    if (ref.verse) url += '#' + ref.verse;
    window.location.href = url;
  }

  function injectNavBar() {
    if (document.getElementById('verse-jump-bar')) return; // 중복 방지

    var bar = document.createElement('div');
    bar.id = 'verse-jump-bar';
    // 배경 없음, 경계선만 아주 얇게
    bar.style.cssText = 'border-bottom:1px solid #e0e0e0;padding:8px 0;';

    // 내부: Bootstrap container + 가운데 정렬
    bar.innerHTML =
      '<div class="container" style="display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;">' +
        '<span style="font-size:13px;color:#555;white-space:nowrap;font-weight:600;">' +
          '&#128214; 구절 바로가기' +
        '</span>' +
        '<input id="verse-jump-input" type="text"' +
          ' placeholder="창 1:1  /  마 3:16  /  Genesis 1:1"' +
          ' style="width:260px;font-size:13px;' +
                 'border:1px solid #ccc;border-radius:4px;padding:4px 10px;outline:none;">' +
        '<button id="verse-jump-btn"' +
          ' style="font-size:13px;padding:4px 14px;border:1px solid #555;border-radius:4px;' +
                 'background:#555;color:#fff;cursor:pointer;white-space:nowrap;">이동</button>' +
      '</div>';

    // 삽입 위치: 메인 페이지는 히어로 섹션(.site-blocks-cover) 바로 뒤,
    //            성경 본문 페이지는 .container.border 바로 앞
    if (isMainPage) {
      var hero = document.querySelector('.site-blocks-cover');
      if (hero && hero.parentNode) {
        hero.parentNode.insertBefore(bar, hero.nextSibling);
      } else {
        var contents = document.querySelector('.contents');
        if (contents) contents.insertBefore(bar, contents.firstChild);
      }
    } else {
      var bibleContainer = document.querySelector('.container.border');
      if (bibleContainer && bibleContainer.parentNode) {
        bibleContainer.parentNode.insertBefore(bar, bibleContainer);
      }
    }

    document.getElementById('verse-jump-btn').addEventListener('click', navigateToVerse);
    document.getElementById('verse-jump-input').addEventListener('keydown', function (e) {
      if (e.key === 'Enter') navigateToVerse();
    });
  }

  // DOM 준비 여부에 따라 즉시 또는 DOMContentLoaded 후에 실행
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectNavBar);
  } else {
    injectNavBar();
  }

})();
