$(document).ready(function () {
    $(".buscador").on('keyup', function (e) {
        if (e.keyCode == 13) {
            alert(window.location.pathname);
        }
    });
});
