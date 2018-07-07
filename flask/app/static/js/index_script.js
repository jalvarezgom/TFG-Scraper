$(document).ready(function () {
    $(".buscador").on('keyup', function (e) {
        if (e.keyCode == 13) {
        	searchButton()
        }
    });
});

function searchButton(){
	url = $("#buscador_input").val(); 
	window.location = "/search?q="+url;
}