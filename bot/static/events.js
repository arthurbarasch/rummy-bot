
function selectRoi(){
    let url = '/select-roi';
    httpGet(url,'json',false,function(data){
    });
}

function solveTable(){
    let url = '/solve';
    httpGet(url,'json',false,function(data){
        boardModified = false;
        endMoveButton.addClass('disabled');
        currMaxScore = data.score
        solution = JSON.parse(data.solution)
        print(solution)
    });
}

function drawRandomTile(){
    let url = '/draw-tile';
    httpGet(url,'json',false,function(){
        print("Draw new tile");
        boardModified = false;
        endMoveButton.addClass('disabled');
    })
}

function addRandomHand(){
    let url = '/add-hand';
    httpGet(url,'json',false,function(){
        print("Add random hand");
        boardModified = false;
        endMoveButton.addClass('disabled');
    })
}

function restartBoard(){
    let url = '/restart';
    httpGet(url,'json',false,function(){
        print("Board restart");
        boardModified = false;
        endMoveButton.addClass('disabled');
    })
}

function endPlayerMove(){
    postData = JSON.stringify({'board': board, 'players': players})
    let url = '/end-move';
    httpPost(url,'json',postData,function(data){
        console.log('Board valid? ' +data.valid)
        if(data.valid){
            boardModified = false;
            endMoveButton.addClass('disabled');
        }
    })
}


function keyPressed(){
    if( keyCode == 32){
        board.push('')
    }
}

function mousePressed(){
    selectedTile = createVector(floor(mouseX/sizeX), floor(mouseY/sizeY)) ;
    boardModified = true;
}

function mouseReleased(){
  let newTileLocation = createVector(floor(mouseX/sizeX),floor(mouseY/sizeY))
  if(newTileLocation.y>=ROWS){ //Moved to player tileset

  }else{
    let index = newTileLocation.y*COLS+newTileLocation.x;
    let tileValue;
    if(selectedTile.y>=ROWS){ //Moved from player tileset
      tileValue = players[selectedPlayer][selectedTile.y-ROWS+selectedTile.x]
      players[selectedPlayer].splice(selectedTile.y-ROWS+selectedTile.x,1) //Remove from player's tileset
    }else{
      tileValue = board[selectedTile.y*COLS+selectedTile.x]
      board.splice(selectedTile.y*COLS+selectedTile.x,1) //Remove from board tileset
    }

    endMoveButton.removeClass('disabled');
    board.splice(index,0,tileValue); //Add to board tileset

  }
  selectedTile = createVector(-1,-1);
   updateBoardScore();
}
