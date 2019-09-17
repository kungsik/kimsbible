// originally written by jcuenod (https://github.com/jcuenod)
const verse_heb = document.querySelector("#verse_heb")

const optAccents = document.querySelector("#optAccents")
const optVowels = document.querySelector("#optVowels")
const optDagesh = document.querySelector("#optDagesh")

const removeAccents = (s) => s.replace(/[\u0590-\u05AF\u05BD]/g,"")
const removeVowels = (s) => s.replace(/[\u05B0-\u05BB]/g,"")
const removeDagesh = (s) => s.replace(/\u05BC/g,"")

const doFix = () => {
    var toReturn = verse_heb.outerHTML
    toReturn = optAccents.checked ? removeAccents(toReturn) : toReturn
    toReturn = optVowels.checked ? removeVowels(toReturn) : toReturn
    toReturn = optDagesh.checked ? removeDagesh(toReturn) : toReturn
    verse_container.innerHTML = toReturn

    localStorage.accent = optAccents.checked ? 'on' : 'off'
    localStorage.vowels = optVowels.checked ? 'on' : 'off'
    localStorage.dagesh = optDagesh.checked ? 'on' : 'off'    

    $.getScript('/static/js/modal_word_api.js')

    // 악센트 관련 체크시 번역본이 사라지는 오류 보정
    if (localStorage.getItem(".kjv") == 'on' ) {
        document.getElementById('kjv').style.display = "block"
    }
    if (localStorage.getItem(".kor") == 'on' ) {
        document.getElementById('kor').style.display = "block"
    } 

    if (horizon == 'on') {
        let currentText = document.location.href.split('/')[3];
        showhorizon(currentText);
    }
}

document.querySelector("#optAccents").addEventListener('change', doFix)
document.querySelector("#optVowels").addEventListener('change', doFix)
document.querySelector("#optDagesh").addEventListener('change', doFix)

if (localStorage.accent == 'on') { 
    document.getElementById("optAccents").checked = true 
    doFix()
}
if (localStorage.vowels == 'on') { 
    document.getElementById("optVowels").checked = true 
    doFix()
}
if (localStorage.dagesh == 'on') { 
    document.getElementById("optDagesh").checked = true 
    doFix()
}