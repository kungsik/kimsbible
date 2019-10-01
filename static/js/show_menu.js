// 캐시 파일(정적파일) 저장시 메뉴를 파이썬 코드로 조정하는 것이 어려우므로 자바스크립트로 메뉴를 처리
// 이 경우 쿠키 문제가 생김. 로그인 상태에서 서버 리셋되면 쿠키는 로그인으로 계속 인식
// 이런 현상의 경우 로그아웃을 한번 눌러주면 로그인관련 쿠키가 초기화 됨. -> 나중에 보완할 필요가 있음.

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

function check_auth() {
    var cookies = document.cookie.split(";");
    var auth = 0;
    var result = '';

    for(var i in cookies) {
        if(cookies[i].search('remember_token') != -1) {
            auth = 1;
        }
    }
    if (auth == 1) {
        result += '<li><a href="/auth/info/">회원정보</a></li><li><a href="/auth/signout/">로그아웃</a></li>';
    }
    else {
        result += '<li><a href="/auth/signup/">회원가입</a></li><li><a href="/auth/signin/">로그인</a></li>';
    }
    return result;
}

var html = '<nav class="site-navigation position-relative text-center" role="navigation">';
html += '<ul class="site-menu main-menu js-clone-nav mr-auto d-none d-lg-block">';

for (var el in menu) {
    html += '<li class="has-children">';
    html += '<a href="#!" class="nav-link">' + el + '</a>';
    html += '<ul class="dropdown">'

    if (el == '회원메뉴') {
        html += check_auth();
    }

    else {
        for (var sub in menu[el]) {
            html += '<li><a href="' + menu[el][sub] + '">' + sub + '</a></li>';
        }
    }

    html += '</ul>'
}

html += '</ul></nav>';


document.getElementById('main-menu').innerHTML = html;