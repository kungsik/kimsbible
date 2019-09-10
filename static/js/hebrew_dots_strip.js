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

    $.getScript('/static/js/modal_word_api.js')
}
document.querySelector("#optAccents").addEventListener('change', doFix)
document.querySelector("#optVowels").addEventListener('change', doFix)
document.querySelector("#optDagesh").addEventListener('change', doFix)