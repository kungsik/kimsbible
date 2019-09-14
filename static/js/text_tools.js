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
	 }
	 else {
		for (var i = 0; i < myelements.length; i++) {
			myelements[i].style.display = "none";
		}
	 }
 }

 function showhorizon(text) {
   let versenodes = document.querySelectorAll('.verseNode');
   let versecontainers = document.querySelectorAll('.verseContainer')
   let transversions = document.querySelectorAll('.transversions')

   if (document.getElementById('showhorizon').checked == true) {
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
     for (var i = 0; i < versenodes.length; i++) {
      versecontainers[i].style.display = "block";
      transversions[i].style.marginTop = "0px";
     }
   }
 }

 function content_print(){
    var initBody = document.body.innerHTML;
    var buttons = document.querySelectorAll('button');

    for (var i = 0; i < buttons.length; i++) {
      buttons[i].style.display = 'none';
    }

    window.onbeforeprint = function(){
        document.body.style.margin = "15mm";
        document.body.innerHTML = document.getElementById('text_body').innerHTML;
    }
    window.onafterprint = function(){
        document.body.innerHTML = initBody;
        window.location.reload();
    }
    window.print();     
  }     