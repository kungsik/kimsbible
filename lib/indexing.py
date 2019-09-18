from whoosh.index import create_in
from whoosh.fields import *

schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
