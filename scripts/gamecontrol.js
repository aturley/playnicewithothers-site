$(document).ready(function() {
    var newGame = function(interval) {
      $.ajax({
        url: "/c4/newgame",
            data:{"interval":interval},
            success: function(data){
            console.log("created new game with interval of " + interval);
          }
        });
    };
    var start = function() {
      $.ajax({
        url: "/c4/startgame",
            success: function(data){
            console.log("started game");
          }
        });
    };
    $("#new10s").click(function(evt){console.log("new 10 s"); newGame(10); });
    $("#new15s").click(function(evt){console.log("new 15 s"); newGame(15);});
    $("#new20s").click(function(evt){console.log("new 20 s"); newGame(20);});
    $("#start").click(function(evt){console.log("start"); start();});
  }
        );
