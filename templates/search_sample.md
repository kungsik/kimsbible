검색 예문
=========
<br>
<font color=red>이 문서는 현재 계속 업데이트 중입니다. 문서상으로 불충분한 내용은 동영상으로도 업데이트할 계획입니다.</font>
<br>

#### 창세기 1, 2장에서 אלהים 단어 검색

```
book book=Genesis  
  chapter chapter=1|2
    word lex_utf8=אלהימ
```

#### 절대형 부정사 + 일반동사 조합 (강조의 의미)

```
verse
  word sp=verb   vt=infa
  <: word sp=verb  
```
- word sp=verb 품사=동사
- vt=infa 시제=절대부정사
- word ... <: word ... 앞에 나온 단어와 뒤에 나온 단어가 바로 붙어서 나옴.
