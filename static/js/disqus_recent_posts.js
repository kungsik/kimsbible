$(document).ready(function() {

	$commentDiv = $("#disqus_recent");
	
	$.get("https://disqus.com/api/3.0/threads/listPosts.json?forum=alpaalrebseonggyeong&thread=7611588846&limit=3&api_key=8C1bWCyMgfsAEm9EDpCgboLD30M3sKHqN0izKBPJp2jgk0ceNxvAJjWsT3MH76k7", function(res, code) {
		//Good response?
		if(res.code === 0) {
			var result = "";
			for(var i=0, len=res.response.length; i<len; i++) {
				var post = res.response[i];
				console.dir(post);
                var html = "<div class='author-box col-sm-3' data-aos='fade-up' style='margin: 10px'>";
                html += "<div class='d-flex mb-4'>";
                html += "<div class='mr-3'>" 
                html += "<img src='" + post.author.avatar.small.permalink + "' alt='Image' class='img-fluid rounded-circle'>";
                html += "</div>"
                html += "<div class='mr-auto text-black'>"
                html += "<a href='"+ post.author.profileUrl + "'>" + post.author.name + "</a>";
				html += "</div></div>"
				
				dots = post.raw_message.length > 150 ? "..." : ""

				html += "<p><a href='/community/#comment-" + post.id + "'>" + post.raw_message.substr(0,150) + dots + "</a></p>";
				html += "<p class='postRef'>" + post.createdAt.split("T")[0] + "</p>";
				html += "</div>";
				
				result+=html;
			}
			$commentDiv.html(result);
		}
	});
});