// Welcome!  This is a dynamically generated listing of as many episodes as I
// find, maintained by a different person than the main page.  Do not contact
// Diamond (The main page's webmaster) with any comments or issues occuring
// regarding this file.  Instead, contact me (Taizo) at the email
// tsa6games@gmail.com with any inqueries.
//
// This page is generated from a number of dailymotion channels which regularly
// post mlp episodes.  An algorithm is used to pick out the relevant episodes as
// well as some basic information about them.  Some episodes are also selected
// by hand and included.
//
// If you are intrested in the server-side source code, shoot me an email and I
// can send it to you, though be warned -- it isn't exactly neat or well
// documented.  You can also see an interactive chart at
// http://tsa6.us.to/mlptkeps
//
// If you host episodes on your own dailymotion channel or run a listing that
// you would like included in the algorith, please contact me and I will add you
// to the list.
console.log("%cAlso, a dynamic listing created from several sources ----->", "font-size:15px;");
console.log("For more information, see http://tsa6.us.to/mlptkeps, contact tsa6games@gmail.com, or look at the comments in the source.");

//Episode Listing:
episodes = /* Dynamic Content */;

// Randomization function that won't return an unavailable episode
// Note:  Each season is equally weighted, and each episode within the selected
// season, but episodes in different seasons have different probabilities of
// being selected.
function random_episode() {
	var season_s = Math.floor(Math.random() * (episodes.length)) + 1;
	var episode = Math.floor(Math.random() * (episodes[season_s - 1].length)) + 1;
	return episodes[season_s - 1][episode - 1].available ? videoPopper(season_s, episode) : random_episode();
}

//Creates "missing episode" frame by modifying the openEpisode function
var missingFrame = document.createElement("iframe");
missingFrame.style.height = "100%";
missingFrame.style.width = "100%";
missingFrame.style.display = "none";
missingFrame.style.border = "0";
missingFrame.class = "video";
innerCont = document.body.getElementsByClassName("inner-cont")[0];
innerCont.insertBefore(missingFrame, innerCont.getElementsByClassName("controls")[0]);
function openEpisode(viddata) {
	dmVideo = document.getElementById("DMVideo");
	$('.episodetitle').text(viddata.title);
	if (episodes[viddata.season - 1][viddata.episode - 1].available) {
		dmVideo.style.display = "inline";
		missingFrame.style.display = "none";
		player = DM.player(dmVideo, {
			video: viddata.embed.replace("//www.dailymotion.com/embed/video/", ""),
			width: "100%",
			height: "100%",
			params: {
				autoplay: true
			}
		});
	} else {
		missingFrame.src = "https://tsa6.tk/webapps/mlptkeps/missing?" + viddata.season + "x" + viddata.episode;
		dmVideo.style.display = "none";
		missingFrame.style.display = "initial";
	}
	$('.vidplayerpopup').fadeIn('fast');
	window.episodeMeta = viddata;
}

//Make sure that episodes listed as unreleased on the main site are marked as released
document.addEventListener("DOMContentLoaded", function(event) { 
    var unreleasedEpisodes = document.getElementsByClassName("mlpepisode_new");
    for(var i = 0; i < unreleasedEpisodes.length; i++) {
        var ep = unreleasedEpisodes[i];
        if(episodes[ep.getAttribute("data-episode-season") - 1]) {
            if(episodes[ep.getAttribute("data-episode-season") - 1][ep.getAttribute("data-episode-number") - 1]) {
                ep.classList.remove("mlpepisode_new");
                ep.classList.add("mlpepisode")
                ep.onclick = function() {
                    openEpisode(videoPopper($(this).data("episode-season"), $(this).data("episode-number")));
                    return false;
                }
		i--;
            }
        }
    }
})