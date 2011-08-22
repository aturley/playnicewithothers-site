(function(win) {
  var World = function (paper, ball) {
    this.paper = paper;
    this.myBall = ball;
    this.otherBalls = {};
    this.heartbeatInterval = 2000;

    win.setInterval(this.sendHeartbeat, this.heartbeatInterval, this);
    win.setInterval(this.cullOthers, this.heartbeatInterval, this);
  };

  World.prototype.addBall = function(id) {
    var circle = paper.circle(-10, -10, 10);
    var ball = new Ball(circle, id);
    return ball;
  };

  World.prototype.sendMyMove = function (move) {
    this._sendMove(this.myBall.id, move);
  };

  World.prototype.sendHeartbeat = function(data) {
    data._sendHeartbeat(data.myBall.id, data.myBall.getPos());
  };

  World.prototype._sendMove = function(id, move) {
  };

  World.prototype._sendHeartbeat = function(id, pos) {
  };

  World.prototype.handleOtherMove = function(move, id) {
    if (id == this.myBall.id) {
      return;
    }
    var movedBall = this.getBall(id) || this.addBall(id);
    movedBall.doMove(move);
  };

  World.prototype.handleOtherHeartbeat = function(id, pos) {
    if (id == this.myBall.id) {
      return;
    }
    var heartbeatBall = this.getBall(id);
    if (!heartbeatBall) {
      this.addBall(id);
      heartbeatBall.setPos(pos);
    }
    heartbeatBall.beatHeart();
  };

  World.prototype.cullOthers = function(data) {
    otherBalls = data.otherBalls;
    for (var key in otherBalls) {
      if (otherBalls.hasOwnProperty(key)) {
        otherBalls[key].decHeart();
        if (otherBalls[key].isDead()) {
          otherBalls[key].uiRep.remove();
          delete otherBalls[key];
        }
      }
    }
  };

  win.World = World;
})(window);
