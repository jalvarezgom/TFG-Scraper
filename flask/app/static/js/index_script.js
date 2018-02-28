$(document).ready(function () {
    $(".buscador").on('keyup', function (e) {
        if (e.keyCode == 13) {
            window.location = "https://www.example.com";
        }
    });
});

function searchButton(){
	window.location = "/search?q=https://www.mediavida.com/id/xeven";
}