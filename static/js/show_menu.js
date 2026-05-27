// 캐시 파일(정적파일) 저장시 메뉴를 파이썬 코드로 조정하는 것이 어려우므로 자바스크립트로 메뉴를 처리
// 서버 /auth/status/ API를 통해 로그인 상태를 확인

var menu = {
    "소개": {
        "사용 안내": "/page/guide/",
        "개발자 소개": "/page/developer/",
        "저작권 안내": "/page/license/"
    },
    "성서본문" : {
        "구약": "/bhsheb/Genesis/1",
        "신약": "/sblgnt/Matthew/1"
    },
    "주석": {
        "소개": "/page/commentary/",
        "오픈주석": "/commentary/list/",
        "클래식주석": "/classic/list/",
        "내오픈주석": "/commentary/mylist/"
    },
    "나눔": {
        "커뮤니티": "/community/",
        "포럼": "/forum/list/"
    },
    "회원메뉴": {
        "회원가입": "/auth/signup/",
        "로그인": "/auth/signin/",
        "회원정보": "/auth/info/",
        "로그아웃": "/auth/signout/"
    }
};

function build_menu(authenticated) {
    var html = '<nav class="site-navigation position-relative text-center" role="navigation">';
    html += '<ul class="site-menu main-menu js-clone-nav mr-auto d-none d-lg-block">';

    for (var el in menu) {
        html += '<li class="has-children">';
        html += '<a href="#!" class="nav-link">' + el + '</a>';
        html += '<ul class="dropdown">';

        if (el == '회원메뉴') {
            if (authenticated) {
                html += '<li><a href="/auth/info/">회원정보</a></li><li><a href="/auth/signout/">로그아웃</a></li>';
            } else {
                html += '<li><a href="/auth/signup/">회원가입</a></li><li><a href="/auth/signin/">로그인</a></li>';
            }
        } else {
            for (var sub in menu[el]) {
                html += '<li><a href="' + menu[el][sub] + '">' + sub + '</a></li>';
            }
        }

        html += '</ul>';
        html += '</li>';
    }

    html += '</ul></nav>';
    document.getElementById('main-menu').innerHTML = html;

    // main.js의 siteMenuClone()이 document.ready에서 동기 실행되므로
    // setTimeout으로 그 이후에 실행하여 중복 방지 + 빈 메뉴 보완
    setTimeout(function() {
        var $mobileBody = $('.site-mobile-menu-body');
        $mobileBody.empty();  // main.js가 복사한 내용 포함 전체 초기화
        $('.js-clone-nav').each(function() {
            $(this).clone().attr('class', 'site-nav-wrap').appendTo($mobileBody);
        });

        // 드롭다운 화살표 버튼 추가
        var counter = 0;
        $('.site-mobile-menu .has-children').each(function() {
            var $this = $(this);
            $this.prepend('<span class="arrow-collapse collapsed">');
            $this.find('.arrow-collapse').attr({
                'data-toggle': 'collapse',
                'data-target': '#collapseItem' + counter
            });
            $this.find('> ul').attr({
                'class': 'collapse',
                'id': 'collapseItem' + counter
            });
            counter++;
        });
    }, 200);
}

// 1. 비로그인 상태로 즉시 메뉴 렌더링 → 딜레이·반짝임 없음
build_menu(false);

// 2. 로그인 확인 후 회원메뉴만 갱신 (로그인 상태일 때만)
$.get('/auth/status/', function(data) {
    if (data.authenticated) {
        build_menu(true);
    }
}).fail(function() {
    // 이미 비로그인 메뉴가 표시되어 있으므로 추가 처리 불필요
});
