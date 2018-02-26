$(document).ready(function () {
    $(".buscador").on('keyup', function (e) {
        if (e.keyCode == 13) {
            window.location = "https://www.example.com";
        }
    });
});

function searchButton(){
	window.location = "http://127.0.0.1:5000/search?q=https://www.mediavida.com/id/xeven";
}