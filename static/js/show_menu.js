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

    // main.js의 siteMenuClone()이 AJAX 완료 전에 실행됐을 수 있으므로
    // 모바일 메뉴 바디를 여기서 직접 재구성
    var $mobileBody = $('.site-mobile-menu-body');
    $mobileBody.empty();
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
}

// 서버에 로그인 상태 확인 후 메뉴 생성
$.get('/auth/status/', function(data) {
    build_menu(data.authenticated);
}).fail(function() {
    build_menu(false);
});
