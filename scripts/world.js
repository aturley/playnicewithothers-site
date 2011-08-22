(function(win) {
  var World = function (paper, ball) {
    this.paper = paper;
    this.myBall = ball;
    this.otherBalls = {};
    this.heartbeatInterval = 2000;
    this.channelName = "ballgame";

    win.setInterval(this.sendHeartbeat, this.heartbeatInterval, this);
    win.setInterval(this.cullOthers, this.heartbeatInterval, this);

    var self = this;

    // setup pub-sub
    PUBNUB.subscribe({
      channel  : this.channelName,
          callback : function(message) { self.messageHandler(message) }
      });
  };

  World.prototype.messageHandler = function (message) {
    if (message.message === "move") {
      this.handleOtherMove(message.ballId, message.move);
    } else if (message.message === "heartbeat") {
      this.handleOtherHeartbeat(message.ballId, message.pos);
    }
  };

  World.prototype.getBall = function(id) {
    return this.otherBalls[id];
  };

  World.prototype.addBall = function(id) {
    var circle = this.paper.circle(-10, -10, 10);
    circle.attr("fill", "#f00");
    circle.attr("stroke", "#f00");

    var ball = new Ball(circle, id);
    this.otherBalls[id] = ball;
    return ball;
  };

  World.prototype.sendMyMove = function (move) {
    this._sendMove(this.myBall.id, move);
  };

  World.prototype.sendHeartbeat = function(data) {
    data._sendHeartbeat(data.myBall.id, data.myBall.getPos());
  };

  World.prototype._sendMove = function(id, move) {
    PUBNUB.publish({
      channel : this.channelName,
          message : {message:"move", ballId:id, move:move}
          });
  };

  World.prototype._sendHeartbeat = function(id, pos) {
    PUBNUB.publish({
      channel : this.channelName,
          message : {message:"heartbeat", ballId:id, pos:pos}
          });
  };

  World.prototype.handleOtherMove = function(id, move) {
    console.log("received move from " + id);
    console.log("my id == " + this.myBall.id);
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
    if (heartbeatBall == undefined) {
      heartbeatBall = this.addBall(id);
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
