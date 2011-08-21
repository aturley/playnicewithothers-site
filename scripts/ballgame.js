(function(win) {
  var BallGame = function(width, height, backgroundImage) {
    var paper = Raphael(document.getElementById("main"), width, height);

    var img = paper.image("/images/burstandtext.png", 0, 0, width, height);

    var field = paper.rect(0, 0, width, height);
    field.attr("fill", "#000000");
    field.attr("stroke", "#000000");
    field.attr("opacity", 0);

    var circle = paper.circle(width / 2, height / 2, 10);
    circle.attr("fill", "#f00");
    circle.attr("stroke", "#f00");

    var myBall = new Ball(circle, Math.random());
    var otherBalls = {};

    var world = new World();

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
    var ballGame = new BallGame(468, 503, "/images/burstandtext.png");
  });
