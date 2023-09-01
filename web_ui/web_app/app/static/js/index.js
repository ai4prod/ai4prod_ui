
function getTableForData(items) {
    var html = '\
    <table class="table">\
        <thead>\
            <tr>\
                <th scope="col">ID</th>\
                <th scope="col">Nome</th>\
                <th scope="col">Anno</th>\
            </tr>\
        </thead>\
        <tbody>';
    items.forEach(function (item) {
        html += '\
        <tr>\
            <th scope="row">' + item.id + '</th>\
            <th>' + item.name + '</th>\
            <th>' + item.year + '</th>\
        </tr>';
    });
    html += '\
        <tbody>\
    </table>';
    return html;
}

function sendBboxToFlask(bbox) {
  $.ajax({
    type: "POST",
    url: "/overlay-teach",
    data: JSON.stringify(bbox),
    contentType:"application/json; charset=utf-8"
  });
}

$(function () {

    var img = $('img');

    var actualWidth = eval($('img').attr('width'));
    var actualHeight = eval($('img').attr('height'));

    $( ".overlay" ).resizable({
        containment: "img",
        handles: "e, n, e, s, w, ne, se, sw, nw",
        stop: function(event, ui) {
          var originalWidth = document.querySelector('img').naturalWidth;
          var originalHeight = document.querySelector('img').naturalHeight;
          var ratioWidth = originalWidth / actualWidth;
          var ratioHeight = originalHeight / actualHeight;
          console.log("x-top: " + ui.position.left + " y-top: " + ui.position.top + " x-bottom: " + ui.size.width + " y-bottom: " + ui.size.height);
          var bbox = {
            "x-top": ui.position.left * ratioWidth, 
            "y-top": ui.position.top * ratioHeight,
            "x-bottom": ui.position.left * ratioWidth + ui.size.width * ratioWidth,
            "y-bottom": ui.position.top * ratioHeight + ui.size.height * ratioHeight};
          console.log(bbox);
          sendBboxToFlask(bbox);
        }
    }).draggable({
        containment: "img",
        stop: function( event, ui ) {
          var originalWidth = document.querySelector('img').naturalWidth;
          var originalHeight = document.querySelector('img').naturalHeight;
          var ratioWidth = originalWidth / actualWidth;
          var ratioHeight = originalHeight / actualHeight;
          console.log("x-top: " + ui.position.left + " y-top: " + ui.position.top + " x-bottom: " + $(event.target).width() + ui.position.left + " y-bottom: " + $(event.target).height() + ui.position.top);
          var bbox = {
            "x-top": ui.position.left * ratioWidth, 
            "y-top": ui.position.top * ratioHeight, 
            "x-bottom": $(event.target).width() * ratioWidth + ui.position.left * ratioWidth, 
            "y-bottom": $(event.target).height() * ratioHeight + ui.position.top * ratioHeight};
          
          console.log(bbox);
          sendBboxToFlask(bbox);
        }
    });

    img.onload = function() {
      alert(this.width + 'x' + this.height);
    }

    //close connect to database
    $("#closeCntDatabase").bind("click", function () {
        

        $.ajax({
            type: "POST",
            url: "/closedb",
            success: function (result) {
                $("#connectionDBStatus").text("NON sei connesso al database e alla telecamera");
                $("#connectionDBStatus").css('color', 'red');
            }
        });
    });
    
    //get data
    $("#getDataFromDatabase").bind("click", function () {
        $.ajax({
            type: "GET",
            url: "/getdbdata",
            success: function (items) {
                $("#dbDataTable").html(getTableForData(items));
            },
            fail: function(result) {
                $("#dbDataTable").html("<p> Non connesso al DB -> Prima clicca per connetterti </p>");
            }
        });
    });

    //connect to database
    $("#openCntDatabase").bind("click", function () {
      $.ajax({
        type: "POST",
        url: "/connectdb",
        success: function (result) {
            $("#connectionDBStatus").text("Connesso al database e alla telecamera");
            $("#connectionDBStatus").css('color', 'green');
        }
      });
    });

    //load dataset
    $("#loadBtn").bind("click", function () {
        var path = $("#folderPath").val();
        var server_data = { folderpath: path };
        $.ajax({
          type: "POST",
          url: "/loadfolder",
          data: JSON.stringify(server_data),
          contentType: "application/json",
          dataType: "json",
          success: function (result) {
            //callback function
            console.log(result["value"]);
            $("#numimages").html(result["len"]);
            $("#totalnumber").html(result["len"]);
          },
        });
    });

    $("#negative").bind("click", function () {
        $.ajax({
          url: "{{ url_for ('home.negative') }}",
          type: "GET",
          success: function (response) {
            console.log(response);
          },
          error: function (xhr) {
            //Do Something to handle error
          },
        });
    });

    $("#positive").bind("click", function () {
        $.ajax({
          url: "{{ url_for ('home.positive') }}",
          type: "GET",
          success: function (response) {
            console.log(response);
          },
          error: function (xhr) {
            //Do Something to handle error
          },
        });
    });

    //incremente index
    $("#next").bind("click", function () {
        $.ajax({
          url: "{{ url_for ('home.get_img_next') }}",
          type: "POST",
          contentType: "application/json",
          dataType: "json",
          success: function (response) {
            console.log("/static/dataset/" + response["imagepath"]);
            console.log(response["annotation"]);
  
            $("#myimg").attr("src", "");
            $("#myimg").attr(
              "src",
              "data:image/" + response["ext"] + ";base64," + response["image"]
            );
  
            $("#currentnumber").html(response["index"] + 1);
  
            if (response["annotation"]) {
              $("#myimg").css({
                "border-color": "#C1E0FF",
                "border-width": "1em",
                "border-style": "solid",
              });
            } else {
              $("#myimg").css({
                "border-color": "#C1E0FF",
                "border-width": "0px",
                "border-style": "solid",
              });
            }
          },
          error: function (xhr) {
            //Do Something to handle error
          },
        });
    });

    //decrement index
    $("#previous").bind("click", function () {
        $.ajax({
          url: "{{ url_for ('home.get_img_previous') }}",
          type: "POST",
          contentType: "application/json",
          dataType: "json",
          success: function (response) {
            console.log("/static/dataset/" + response["imagepath"]);
            console.log(response["annotation"]);
            $("#myimg").attr("src", "");
            $("#myimg").attr(
              "src",
              "data:image/" + response["ext"] + ";base64," + response["image"]
            );
  
            $("#currentnumber").html(response["index"] + 1);
  
            if (response["annotation"]) {
              $("#myimg").css({
                "border-color": "#C1E0FF",
                "border-width": "1em",
                "border-style": "solid",
              });
            } else {
              $("#myimg").css({
                "border-color": "#C1E0FF",
                "border-width": "0px",
                "border-style": "solid",
              });
            }
          },
          error: function (xhr) {
            //Do Something to handle error
          },
        });
    });
});