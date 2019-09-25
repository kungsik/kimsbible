# 페이지 인덱싱 라이브러리

import os
from bs4 import BeautifulSoup
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser

class Indexing:
    def __init__(self):
        self.ix = None
        self.index_path = "kimsbible/static/cached/indexed/"
        self.schema = Schema(
            title=TEXT(stored=True), 
            path=ID(stored=True), 
            content=TEXT(stored=True)
        )
        if not os.path.exists(self.index_path):
            os.mkdir(self.index_path)
            self.ix = create_in(self.index_path, self.schema)
            self.index_files = True
            self.writer = self.ix.writer()
        else:
            self.ix = open_dir(self.index_path) 
        
        self.searcher = self.ix.searcher()
        self.parser = QueryParser("content", self.ix.schema)

    #신약(sblgnt) 구약(bhsheb)을 나누어서 인덱싱 타이틀 생성 
    def build_index(self, text):
        location = "kimsbible/static/cached/" + text
        basicroute = "/" + text
        for i in os.listdir(location):
            with open(location + "/" + i, encoding='utf8') as fp:
                filename = i.split(".")
                book = filename[0].split("-")[0]
                chp = filename[0].split("-")[1]
                textroute = basicroute + book + "/" + str(chp)
                soup = BeautifulSoup(fp, 'html.parser')
            content = soup.find("div", {"id": "verse_container"})
            self.writer.add_document(title=i, path=textroute, content=content.get_text())
        self.writer.commit()
        return "indexed"
    
    def search_index(self, word):
        result = []
        query = self.parser.parse(word)
        results = self.searcher.search(query)
        for r in results:
            result.append(r)
        return result


indexing = Indexing()
# indexing.build_index('bhsheb')
print(indexing.search_index(str('모세', "utf-8")))