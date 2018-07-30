$(window).on('load', function(){
    liff.init(function (data) {
        $("#userId").text(data.context.userId);
        $("#viewType").text(data.context.viewType);
    }, function(error) {
        console.log("error: " + error);
        print("error: " + error);
    });
});

$("#openWindow").click(function() {
    alert('openWindow clicked!!');
    liff.openWindow(
        {
            url: "https://line.me"
        }
    );
})