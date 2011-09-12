dddd = null;

(function (win) {
  var Display = function(numberOfButtons) {
    var spacing = 10;
    var lmargin = 10;
    var rmargin = 10;
    var tmargin = 10;
    var bmargin = 10;
    var boxHeight = 40;
    var boxWidth = 40;
    // create raphel space
    var totalWidth = this.numberOfButtons * boxWidth + rmargin + lmargin + (this.numberOfButtons - 1) * spacing;
    var totalHeight = tmargin + bmargin + boxHeight;

    this.numberOfButtons = numberOfButtons;
    this.paper = Raphael("display", totalWidth, totalHeight);
    this.channelToken = null;
    var display = this;
    $.ajax({
      url: "/c4/channelbroker",
          data:{user_id:(new User().userId)},
          success: function(data){
          console.log("got channel id " + data);
          channelToken = $.parseJSON(data).token;
          display.setupChannel(channelToken);
        }
      });
  };

  Display.prototype.setupChannel = function(channelToken) {
    var channel = new goog.appengine.Channel(channelToken);
    var handler = {
      'onopen': function() {},
      'onmessage': function(data) {console.log("got data " + data.data);},
      'onerror': function() {},
      'onclose': function() {}
    };
    var socket = channel.open(handler);
  };

  Display.prototype.draw = function() {
    var spacing = 10;
    var lmargin = 10;
    var rmargin = 10;
    var tmargin = 10;
    var bmargin = 10;
    var boxHeight = 40;
    var boxWidth = 40;
    // create raphel space
    var totalWidth = this.numberOfButtons * boxWidth + rmargin + lmargin + (this.numberOfButtons - 1) * spacing;
    var totalHeight = tmargin + bmargin + boxHeight;

    var paper = this.paper;
    // draw boxes
    var backing = paper.rect(0, 0, totalWidth, totalHeight, 5);
    backing.attr("fill", "#aaa")
    backing.attr("stroke", "#aaa")
  
    var b = null;
    var top = tmargin;
    var left = lmargin;
    var i = 0;
    var buttonList = [];
    for (i = 0; i < this.numberOfButtons; i++) {
      b = paper.rect(left, top, boxWidth, boxHeight, 5);
      b.attr("fill", "#a33");
      b.attr("stroke", "#a33");
      buttonList.push(b);
      left += boxWidth + lmargin;
    }

    for (i = 0; i < this.numberOfButtons; i++) {
      b = buttonList[i];
      (function(b, i) {
        b.node.onclick = function () {
          b.attr("fill", "#f00");
          b.attr("stroke", "#f00");
          var other = 0;
          var otherButton;
          for(other = 0; other < buttonList.length; other++) {
            if (other != i) {
              otherButton = buttonList[other];
              otherButton.attr("fill", "#a33");
              otherButton.attr("stroke", "#a33");
            }
          }
          $.ajax({
            url: "/c4/controllermessage",
                data:{user_id:(new User().userId), vote:i},
                success: function(data){
                console.log("successful vote: " + data);
              }
            });
          console.log((new User()).userId);
        };
      })(b, i);
    }
  };

  win.Display = Display;
})(window);

$(document).ready(function() {
    var display = new Display();
    display.draw();
  });
