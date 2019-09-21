function initialize(kml) {
    var map = new google.maps.Map(document.getElementById("map-canvas"), {
      center: {
        lat: 31.7833,
        lng: 35.2167
      },
      zoom: 8,
      mapTypeId: google.maps.MapTypeId.SATELLITE
    });
    var layer = new google.maps.KmlLayer({
      url: kml,
      preserveViewport: false
    });
    layer.setMap(map);
  }
 
 function showTrans(transclassname, button_id) {
	 let myelements = document.querySelectorAll(transclassname);
	 if (document.getElementById(button_id).checked == true) {
		for (var i = 0; i < myelements.length; i++) {
			myelements[i].style.display = "block";
    }
    localStorage.setItem(transclassname, "on");
	 }
	 else {
		for (var i = 0; i < myelements.length; i++) {
			myelements[i].style.display = "none";
    }
    localStorage.setItem(transclassname, "off");
	 }
 }

 function showhorizon(text) {
   let versenodes = document.querySelectorAll('.verseNode');
   let versecontainers = document.querySelectorAll('.verseContainer')
   let transversions = document.querySelectorAll('.transversions')

   if (document.getElementById('showhorizon').checked == true) {
     
     localStorage.setItem("horizon", "on");

     for (var i = 0; i < versenodes.length; i++) {
      versecontainers[i].style.display = "flex";
      versenodes[i].style.flex = "1";
      transversions[i].style.flex = "1";

      if (text == 'bhsheb') {
        versenodes[i].style.paddingLeft = "10px";
        transversions[i].style.paddingRight = "10px";
      }

      else {
        versenodes[i].style.paddingRight = "10px";
        transversions[i].style.paddingLeft = "10px";
        transversions[i].style.marginTop = "-10px";
      }
     }
   }
   else {
     
     localStorage.setItem("horizon", "off");

     for (var i = 0; i < versenodes.length; i++) {
      versecontainers[i].style.display = "block";
      transversions[i].style.marginTop = "0px";
     }
   }
 }

 function content_print(bookname){
    var initBody = document.body.innerHTML;
    var buttons = document.querySelectorAll('button');

    var path = location.pathname.split('/');
    var book = path[2];

    var bookname_korean = bookname[book];

    if (path[3]) {
      var chapter = path[3];
    }
    else {
      var chapter = '1';
    }

    document.getElementById('selector_title').style.display = 'none';
    document.getElementById('printing_title').innerHTML = '<h3>' + bookname_korean + ' ' + chapter + '장</h3>';

    for (var i = 0; i < buttons.length; i++) {
      buttons[i].style.display = 'none';
    }

    window.onbeforeprint = function(){
        document.body.innerHTML = document.getElementById('text_body').innerHTML;
    }
    window.onafterprint = function(){
        document.body.innerHTML = initBody;
        window.location.reload();
    }
    window.print();     
  }     

let kor = localStorage.getItem(".kor");
let kjv = localStorage.getItem(".kjv");
let horizon = localStorage.getItem("horizon");
let currentText = document.location.href.split('/')[3];

if (horizon == 'on') {
  document.getElementById('showhorizon').checked = true;
  showhorizon(currentText);
}
else {
  document.getElementById('showhorizon').checked = false;
  showhorizon(currentText);
}

if (kor == 'on') {
  document.getElementById('showkor').checked = true;
  showTrans(".kor", 'showkor');
}
else {
  document.getElementById('showkor').checked = false;
  showTrans(".kor", 'showkor');
}

if (kjv == 'on') {
  document.getElementById('showkjv').checked = true;
  showTrans(".kjv", 'showkjv');
}
else {
  document.getElementById('showkjv').checked = false;
  showTrans(".kjv", 'showkjv');
}

// 초기 스토리지 세팅: 한글번역 보이기, 영어번역 숨기기
if (!kjv && !kor) {
  localStorage.setItem(".kor", "on")
  document.getElementById('showkor').checked = true; 
  showTrans(".kor", 'showkor');
}
