(function(win) {
  var Goal = function(uiRep, id) {
    this.uiRep = uiRep;
    this.id = id;
  };

  Goal.prototype._getDistance = function(x1, y1, x2, y2) {
    var deltax = x1 - x2;
    var deltay = y1 - y2;
    return Math.sqrt(deltax * deltax - deltay * deltay);
  };

  Goal.prototype.isInsideGoal = function(x, y) {
    return this._getDistance(x, y) < this.uiRep.attr("width");
  };

  window.Goal = Goal;
})(window);
