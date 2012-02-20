(function(win) {
  var CountdownTimer = function(width) {
    this.rect = null;
    this.width = width;
    this.height = 50;
    this.color = "#f2a";
  }
  CountdownTimer.prototype.initPaper = function(paper) {
    this.rect = paper.rect(0, 0, this.width, this.height, 5);
    this.rect.attr("fill", this.color);
    this.rect.attr("stroke", this.color);
  };

  CountdownTimer.prototype.countdown = function(millis) {
    this.rect.attr("width", this.width);
    this.rect.animate({
        "1%": {width: this.width},
          "100%": {width: 0}
      }, millis);
  };

  win.CountdownTimer = CountdownTimer;
})(window)
