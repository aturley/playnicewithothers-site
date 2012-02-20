(function (win) {
  var Display = function() {
    this.board = new Board({color:"red"}, {color:"black"}, {color:"white"});
    this.boardPaper = Raphael("display", this.board.totalWidth, this.board.totalHeight);
    this.board.initPaper(this.boardPaper);
    this.won = false;

    this.voting = new Voting();
    this.votingPaper = Raphael("voting", this.voting.totalWidth, this.voting.totalHeight);
    this.voting.initPaper(this.votingPaper);

    this.timer = new CountdownTimer(this.voting.totalWidth);
    this.timerPaper = Raphael("countdowntimer", this.voting.totalWidth, this.timer.height);
    this.timer.initPaper(this.timerPaper);

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

  Display.prototype.kickTimer = function() {
    $.ajax({
      url: "/timer",
          data:{game:"c4"},
      });    
  };

  Display.prototype.setupChannel = function(channelToken) {
    var display = this;
    var channel = new goog.appengine.Channel(channelToken);
    var handler = {
      'onopen': function() {},
      'onmessage': function(data) {
        dataObj = $.parseJSON(data.data);
        console.log("got data " + dataObj);
        console.log("got data.type " + dataObj.type);
        if (dataObj.type == "vote") {
          display.handleVote(dataObj.user_id, dataObj.vote);
        } else if (dataObj.type == "newgame") {
          display.handleNewGame();
        } else if (dataObj.type == "startgame") {
          display.handleStartGame(dataObj.interval);
        } else if (dataObj.type == "playercount") {
          display.handlePlayerCount(dataObj.count);
        } else if (dataObj.type == "votes") {
          display.handleVotes(dataObj.votes);
        } else if (dataObj.type == "timer") {
          display.handleTimer();
        } else if (dataObj.type == "turnfinished") {
          display.handleTurnFinished(dataObj.board, dataObj.turn, dataObj.winner, dataObj.winning, dataObj.interval);
        }
      },
      'onerror': function() {},
      'onclose': function() {}
    };
    var socket = channel.open(handler);
  };

  Display.prototype.handleVote = function(user_id, vote) {
    console.log("" + user_id + " voted for " + vote);
  };

  Display.prototype.handleVotes = function(votes) {
    console.log("votes: " + votes);
    this.voting.drawVotes(votes);
  };

  Display.prototype.handleTimer = function() {
    console.log("timer");
  };

  Display.prototype.handleNewGame = function() {
    console.log("clearing board");
    this.board.clearBoard();
    this.won = false;
    this.showTeamTurn("");
    this.showTurns(0);
    this.showPlayerCount(0);
    this.showWinner("");
  };

  Display.prototype.handleStartGame = function(interval) {
    console.log("starting game");
    this.showTeamTurn("black");
    this.timer.countdown(interval * 1000)
  };

  Display.prototype.handlePlayerCount = function(count) {
    console.log("playercount");
    this.showPlayerCount(count);
  };

  Display.prototype.handleTurnFinished = function(board, turn, winner, winning, interval) {
    if (!this.won) {
      this.board.drawString(board);
      this.voting.clearVotes();

      this.showTurns(turn + 1);

      if (winner != null) {
        this.showWinner(winner);
        this.won = true;
      } else {
        this.showTeamTurn(["black", "red"][(turn + 1) % 2]);
        this.timer.countdown(interval * 1000)
      }
    }
  };

  Display.prototype.showWinner = function(winner) {
    if (winner) {
      $("#winner").html(winner + " wins!");
    } else {
      $("#winner").html("");
    }
  };

  Display.prototype.showTeamTurn = function(team) {
    if (team == "") {
      $("#teamturn").html("");
    } else {
      $("#teamturn").html(" " + team + "'s turn");
    }
  };

  Display.prototype.showPlayerCount = function(count) {
    $("#playercount").html("Players: " + count);
  };

  Display.prototype.showTurns = function(turns) {
    $("#turns").html("Total turns: " + turns);
  };

  Display.prototype.draw = function() {
  };

  Display.prototype.drawx = function() {
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

    var paper = this.paper;
    // draw boxes
    console.log("drawing " + totalWidth + " " + totalHeight);
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
    var display = new Display(7);
    display.draw();
    // display.kickTimer();
  });
