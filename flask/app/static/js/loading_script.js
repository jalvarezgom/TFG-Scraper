$(document).ready(function () {
    


    setInterval(function(){ 
        $.getJSON("http://127.0.0.1:5000/status",function(data){
            if(data['status']=true){
                window.location = "https://www.example.com";
            }
        });
    }, 20000);
});
