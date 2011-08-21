(function(win) {
  var Move = function(startx, starty, endx, endy, rate) {
    this.startx = startx;
    this.starty = starty;
    this.endx = endx;
    this.endy = endy;
    this.rate = rate;
    var deltax = startx - endx;
    var deltay = starty - endy;
    this.distance = Math.sqrt(deltax * deltax + deltay * deltay);
    this.time = this.distance / rate;
  };

  win.Move = Move;
})(window);
