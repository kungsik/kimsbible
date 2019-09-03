from tf.fabric import Fabric
from flask import render_template, request, url_for
from kimsbible import app
from kimsbible.bhsheb import api
from kimsbible.bhsheb import get_strong, get_kor_hgloss
from collections import OrderedDict
from kimsbible.lib import lib as kb
from kimsbible import bhsheb_stat as stat

api.makeAvailableIn(globals())

@app.route('/studytools/reading/', methods=['GET', 'POST'])
def studytools():
    if request.method == 'POST':
        rangeCode = request.form['rangeCode']
        nodeList = stat.codetorange(rangeCode)
        rangeStr = stat.codetostr(rangeCode, stat.bookListKor)
        sectionTitle = rangeStr.split("; ")
        
        if nodeList == False: return False
        
        result = ''
        i = 0

        # for title in sectionTitle:
        #     result = "<h4>" + title + "</h4>"
        for node in nodeList:
            section = T.sectionFromNode(node)
            chpvrs = str(section[1]) + ":" + str(section[2])
            result += '<span class=chpvrs>' + chpvrs + '</span> <span class="verse">' + T.text(L.d(node, otype='word')) + '</span>'
    
        return result

    else:
        return render_template('studytools_reading.html')
