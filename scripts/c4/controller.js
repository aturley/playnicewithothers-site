(function (win) {
  var Buttons = function(numberOfButtons) {
    this.numberOfButtons = numberOfButtons;
  };

  Buttons.prototype.drawButtons = function() {
    var spacing = 10;
    var lmargin = 10;
    var rmargin = 10;
    var tmargin = 10;
    var bmargin = 10;
    var boxHeight = 40;
    var boxWidth = 40;
    // create raphael space
    var totalWidth = this.numberOfButtons * boxWidth + rmargin + lmargin + (this.numberOfButtons - 1) * spacing;
    var totalHeight = tmargin + bmargin + boxHeight;

    var paper = Raphael("controller", totalWidth, totalHeight);
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
            url: "/c4/vote",
                type:"POST",
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

  win.Buttons = Buttons;
})(window);

$(document).ready(function() {
    var buttons = new Buttons(7);
    buttons.drawButtons();
    $.ajax({
      url: "/c4/team",
          data:{user_id:(new User().userId)},
          success: function(data){
          console.log("got data " + data);
          dataObj = $.parseJSON(data);
          console.log("team: " + dataObj.team);
          $("#team").html("your team is: " + dataObj.team);
        }
      });

  });
