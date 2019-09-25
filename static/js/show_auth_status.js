// 캐시 파일(정적파일) 저장시 파이썬 코드로 로그인 정보 가져오는데에 문제가 생기므로 자바스크립트로 처리함.
var cookies = document.cookie.split(";");
var auth = 0;
var html = '';

for(var i in cookies) {
    if(cookies[i].search('remember_token') != -1) {
        auth = 1;
    }
}

if (auth == 1) {
    html += '<li><a href="/auth/signout/">로그아웃</a></li>';
}
else {
    html += '<li><a href="/auth/signup/">회원가입</a></li><li><a href="/auth/signin/">로그인</a></li>';
}

document.getElementById('auth').innerHTML = html;