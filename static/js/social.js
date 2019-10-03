Kakao.init('062c1050eef5ed2c680d281999db675a');

function sendLinkKakao(){
    Kakao.Link.sendDefault({
      objectType: 'feed',
      content: {
        title: '{{ post.title }}',
        description: '{{ post.content|bs4process|truncatewords:15 }}',
        imageUrl: '{{ post.content|bs4imagepath|full_url }}',
        link: {
          mobileWebUrl: '{{ request.build_absolute_uri }}',
          webUrl: '{{ request.build_absolute_uri }}'
        }
      },
      buttons: [       
        {
          title: '링크 열기',
          link: {
            mobileWebUrl: '{{ request.build_absolute_uri }}',
            webUrl: '{{ request.build_absolute_uri }}'
          }
        }
      ]
    }); 
}