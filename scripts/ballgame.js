(function(win) {
  var BallGame = function() {
    var paper = Raphael(document.getElementById("main"), 468, 503);
    var img = paper.image("/images/burstandtext.png", 0, 0, 468, 503);
    var field = paper.rect(0, 0, 468, 503);
    field.attr("fill", "#000000");
    field.attr("stroke", "#000000");
    field.attr("opacity", 0);
    // Creates circle at x = 50, y = 40, with radius 10
    var circle = paper.circle(50, 40, 10);
    // Sets the fill attribute of the circle to red (#f00)
    circle.attr("fill", "#f00");

    // Sets the stroke attribute of the circle to white
    circle.attr("stroke", "#f00");

    var myBall = new Ball(circle);

    $("#main").click(function (e) {
        var posX = $(this).offset().left;
        var posY = $(this).offset().top;
        var x = e.pageX - posX;
        var y = e.pageY - posY;
        var move = myBall.createMove(x, y);
        myBall.doMove(move);
      });
  };

  win.BallGame = BallGame;
})(window);

$(document).ready(function() {
    var ballGame = new BallGame();
  });
