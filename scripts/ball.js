(function(win) {
  var Ball = function(uiRep) {
    this.ballPixPerSecond = 100;
    this.uiRep = uiRep;
  };

  Ball.prototype.moveTo = function(x, y, cb) {
    this.uiRep.stop();
    var moveTime = this._timeToNewPos(this.uiRep.attr("cx"), this.uiRep.attr("cy"), x, y);
    this.uiRep.animate({"100%":{cx:x, cy:y, callback:cb}}, moveTime * 1000);
  };

  Ball.prototype.createMove = function (x, y) {
    var move = new Move(this.uiRep.attr("cx"), this.uiRep.attr("cy"), x, y, this.ballPixPerSecond);
    return move;
  };

  Ball.prototype.doMove = function(move, cb) {
    this.uiRep.stop();
    this.uiRep.animate({"100%":{cx:move.startx, cy:move.starty, callback:cb}}, 0);
    this.uiRep.animate({"100%":{cx:move.endx, cy:move.endy, callback:cb}}, move.time * 1000);
  };

  Ball.prototype._timeToNewPos = function (oldx, oldy, newx, newy) {
    var deltax = oldx - newx;
    var deltay = oldy - newy;
    var newDistance = Math.sqrt(deltax * deltax + deltay * deltay);
    return newDistance / this.ballPixPerSecond;
  };

  win.Ball = Ball;
})(window);
