(function (win) {
  var Voting = function() {
    this.numberOfChoices = 7;
    this.votes = new Array(this.numberOfChoices);
    this.voteMarkers = new Array(this.numberOfChoices);
    this.markerWidth = 40;
    this.markerHeight = 40;
    this.markerSpacing = 10;
    this.hMargin = 10;
    this.vMargin = 10;
    this.totalWidth = this.hMargin * 2 + (this.markerWidth + this.markerSpacing) * this.numberOfChoices - this.markerSpacing;
    this.totalHeight = this.vMargin * 2 + this.markerHeight;
  };

  Voting.prototype.initPaper = function(paper) {
    var backing = paper.rect(0, 0, this.totalWidth, this.totalHeight, 5);
    backing.attr("fill", "#fff")
    backing.attr("stroke", "#fff")

    var bg = null;
    var b = null;
    var top = this.vMargin;
    var left = this.hMargin;
    var i = 0;
    for (i = 0; i < this.numberOfChoices; i++) {
      b = paper.rect(left, top, this.markerWidth, this.markerHeight, 5);
      b.attr("fill", "#00f");
      b.attr("stroke", "#00f");

      bg = paper.rect(left, top, this.markerWidth, this.markerHeight, 5);
      bg.attr("fill", "#fff");
      bg.attr("stroke", "#fff");

      this.voteMarkers[i] = bg;

      left += this.markerWidth + this.hMargin;
    }
  };

  Voting.prototype.clearVotes = function() {
    var i = 0;
    var b = null;
    for (i = 0; i < this.numberOfChoices; i++) {
      b = this.voteMarkers[i];
      b.attr("height", this.markerHeight);
    }
  }

  Voting.prototype.drawVotes = function(votes) {
    var i;
    var b;
    var color;
    var totalVotes = 0;

    for (i = 0; i < votes.length; i++) {
      totalVotes += votes[i];
    }
    console.log("total of " + totalVotes + " votes");

    for (i = 0; i < this.numberOfChoices; i++) {
      b = this.voteMarkers[i];
      b.attr("height", this.markerHeight - (this.markerHeight * votes[i] / totalVotes));
    }
  };

  win.Voting = Voting;
})(window)
