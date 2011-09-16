(function (win) {
  var Board = function(redPiece, blackPiece, nonePiece) {
    this.uiBoard = null;
    this.pieces = {red:redPiece, black:blackPiece, none:nonePiece}
    this.columns = 7;
    this.rows = 6;
    this.pieceRadius = 20;
    this.pieceSpacing = 10;
    this.totalWidth = (this.pieceRadius * 2 + this.pieceSpacing) * this.columns + this.pieceSpacing;
    this.totalHeight = (this.pieceRadius * 2 + this.pieceSpacing) * this.rows + this.pieceSpacing;
    this.boardColor = "#00f";
    this.spots = [];
    this.uiSpots = [];
  };

  Board.prototype.initPaper = function(paper) {
    this.initBoard(paper);
    this.initPieces(paper);
  };

  Board.prototype.initBoard = function(paper) {
    this.uiBoard = paper.rect(0, 0, this.totalWidth, this.totalHeight, 5);
    this.uiBoard.attr("fill", this.boardColor);
    this.uiBoard.attr("stroke", this.boardColor);
  };

  Board.prototype.initPieces = function(paper) {
    var i;
    var j;
    var downPos;
    var leftPos = this.pieceSpacing + this.pieceRadius;
    var tempRow;
    var tempCircle;
    for (i = 0; i < this.columns; i++) {
      downPos = this.pieceSpacing + this.pieceRadius;
      tempRow = [];
      tempUIRow = [];
      for (j = 0; j < this.rows; j++) {
        tempRow.push(this.nonePiece);
        tempCircle = paper.circle(leftPos, downPos, this.pieceRadius);
        tempCircle.attr("stroke", this.pieces.none.color);
        tempCircle.attr("fill", this.pieces.none.color);
        tempUIRow.push(tempCircle);
        downPos += this.pieceSpacing + 2 * this.pieceRadius;
      }
      this.spots.push(tempRow);
      this.uiSpots.push(tempUIRow);
      leftPos += this.pieceSpacing + 2 * this.pieceRadius;
    }
  };
  Board.prototype.drawString = function(stringBoard) {
    console.log("stringBoard = " + stringBoard);
    var i;
    var j;
    var piece;
    var color;
    for (i = 0; i < this.columns; i++) {
      for (j = 0; j < this.rows; j++) {
        piece = stringBoard.substring(j * this.columns + i, j * this.columns + i + 1);
        if (piece == "_") {
          color = this.pieces.none.color;
        } else if (piece == "b") {
          color = this.pieces.black.color;
        } else if (piece == "r") {
          color = this.pieces.red.color;
        }
        this.uiSpots[i][j].attr("fill", color)
        this.uiSpots[i][j].attr("stroke", color)
      }
    }
  };
  
  win.Board = Board;
})(window);
