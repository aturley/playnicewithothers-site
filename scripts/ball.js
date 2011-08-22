(function(win) {
  var Ball = function(uiRep, id) {
    this.ballPixPerSecond = 100;
    this.uiRep = uiRep;
    this.id = id;
    this.heartbeatReserve = 2;
  };

  Ball.prototype.getPos = function() {
    return {x:this.uiRep.attr("cx"), y:this.uiRep.attr("cy")};
  };

  Ball.prototype.setPos = function(pos) {
    this.uiRep.stop();
    this.uiRep.animate({"100%":{cx:pos.x, cy:pos.y, callback:cb}}, 0);
    return this;
  };

  Ball.prototype.beatHeart = function() {
    this.heartbeatReserve += 1;
  };

  Ball.prototype.decHeart = function() {
    this.heartbeatReserve -= 1;
  };

  Ball.prototype.isDead = function() {
    return this.heartbeatReserve > 0;
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
