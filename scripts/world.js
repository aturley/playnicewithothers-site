(function(win) {
  var World = function (ball) {
    this.myBall = ball
    this.otherBalls = {};
  };

  World.prototype.sendMyMove = function (move) {
  };

  World.prototype.sendHeartbeat = function() {
  };

  World.prototype.handleOtherMove = function(move, id) {
  };

  World.prototype.handleOtherHeartbeat = function(id) {
  };

  World.prototype.cullOthers = function() {
  };

  win.World = World;
})(window);
