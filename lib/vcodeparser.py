bookList = ["null", "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges",
        "1_Samuel", "2_Samuel", "1_Kings", "2_Kings", "Isaiah", "Jeremiah", "Ezekiel",
        "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
        "Haggai", "Zechariah", "Malachi", "Psalms", "Job", "Proverbs", "Ruth", "Song_of_songs",
        "Ecclesiastes", "Lamentations", "Esther", "Daniel", "Ezra", "Nehemiah", "1_Chronicles",
        "2_Chronicles", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1_Corinthians", 
        "2_Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians", "1_Thessalonians", 
        "2_Thessalonians", "1_Timothy", "2_Timothy", "Titus", "Philemon", "Hebrews", "James", 
        "1_Peter", "2_Peter", "1_John", "2_John", "3_John", "Jude", "Revelation"]


bookListKor = ["null", "창세기", "출애굽기", "레위기", "민수기", "신명기", "여호수아", "사사기", 
        "사무엘상", "사무엘하", "열왕기상", "열왕기하", "이사야", "예레미야", "에스겔", 
        "호세아", "요엘", "아모스", "오바댜", "요나", "미가", "나훔", "하박국", "스바냐", 
        "학개", "스가랴", "말라기", "시편", "욥기", "잠언", "룻기", "아가",
        "전도서", "예레미야애가", "에스더", "다니엘", "에스라", "느헤미야", "역대상", 
        "역대하", "마태복음", "마가복음", "누가복음", "요한복음", "사도행전", "로마서", "고린도전서",
        "고린도후서", "갈라디아서", "에베소서", "빌립보서", "골로새서", "데살로니가전서", "데살로니가후서",
        "디모데전서", "디모데후서", "디도서", "빌레본서", "히브리서", "야고보서", "베드로전서", "베드로후서",
        "요한1서", "요한2서", "요한3서", "유다서", "요한계시록"]

bookListKorAbbr = ["null", "창", "출", "레", "민", "신", "수", "삿", "삼상", "삼하", "왕상", "왕하",
        "사", "렘", "겔", "호", "욜", "암", "옵", "욘", "미", "나", "합", "습", "학", "슥", "말",
        "시", "욥", "잠", "룻", "아", "전", "애", "에", "단", "스", "느", "대상", "대하", "마", "막",
        "눅", "요", "행", "롬", "고전", "고후", "갈", "엡", "빌", "골", "살전", "살후", "딤전", "딤후",
        "딛", "몬", "히", "약", "벧전", "벧후", "요일", "요이", "요삼", "유", "계"]

def codetostr(code, bookList):
    code = code.replace(" ", "")
    codeSplit1 = code.split(';')
    strvrs = ""
    i = 0
    for c1 in codeSplit1:
        codeSplit2 = c1.split('-')
        if i > 0:
            strvrs += "; "
            i = 0

        for c2 in codeSplit2:
            if len(c2) != 7 and len(c2) != 8:
                return False
            if i == 1:
                strvrs += "~"
            if len(c2) == 7:
                strvrs += bookList[int(c2[0])] + " " + str(int(c2[-6] +  c2[-5] +  c2[-4])) + ":" + str(int(c2[-3] +  c2[-2] +  c2[-1]))
            elif len(c2) == 8:
                strvrs += bookList[int(c2[0] + c2[1])] + " " + str(int(c2[-6] +  c2[-5] +  c2[-4])) + ":" + str(int(c2[-3] +  c2[-2] +  c2[-1]))
            i = i + 1
    return strvrs

#text-fabric section to code
def nodetocode(section, bookList):
    bookcode = bookList.index(section[0])
    chpcode = str(section[1])
    versecode = str(section[2])

    result = str(bookcode)

    if len(chpcode) == 1:
        result = result + '00' + chpcode
    elif len(chpcode) == 2:
        result = result + '0' + chpcode
    else:
        result = result + chpcode

    if len(versecode) == 1:
        result = result + '00' + versecode
    elif len(chpcode) == 2:
        result = result + '0' + versecode
    else:
        result = result + versecode
    
    return result