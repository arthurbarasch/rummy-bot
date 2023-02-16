function httpGetError(){
    console.log('ERROR: on http GET')
}

function updateGameState(){
    if(frameCount%20==1 && !boardModified && !solution){
        let url = '/game-state';
        httpGet(url,'json',false,setGameState, httpGetError);
    }
}

function setGameState(state){
    board = [];
    if(!state || !state.board) return
    for(let run of state.board.runs){
        board.push(...run)
        board.push('')
    }

    for(let group of state.board.groups){
        board.push(...group)
        board.push('')
    }

    lastPlayer = selectedPlayer
    selectedPlayer = state.playerTurn;
    if(selectedPlayer != lastPlayer){
        displayMessage("Player "+(selectedPlayer+1)+",\nit's your turn",1800)
    }

    players = state.players;
    drawPileSize = state.drawPileSize
    buttons[0].html('Draw tile<br>('+drawPileSize+')')
    updateBoardScore();
}

function selectRoi(){
    let url = '/select-roi';
    httpGet(url,'json',false,function(data){
    });
}

function solveTable(){
    let url = '/solve';
    httpGet(url,'json',false,function(data){
        boardModified = false;
        disableEndMoveButton();
        currMaxScore = data.score
        solution = data

        print('Score array:')
        print(data.scoreArray)
    });
}

let otherSolutions = []
function calculateOtherSolutions(){
    if(otherSolutions.length>0){
        let s = otherSolutions.pop()
        solution = s[1]
        currMaxScore = s[0];
        return;
    }


    let url = '/other-solutions';
    httpGet(url,'json',false,function(data){
        boardModified = false;
        disableEndMoveButton();

        otherSolutions = JSON.parse(data.solutions)
    });
}

function drawRandomTile(){
    let url = '/draw-tile';
    httpGet(url,'json',false,function(){
        print("Draw new tile");
        boardModified = false;
        disableEndMoveButton();
    })
}

function newGame(){
    let url = '/restart';
    httpGet(url,'json',false,function(){
        print("Board restart");
        boardModified = false;
        disableEndMoveButton();
    })
}

function newGameAI(){
    let url = '/restart-ai';
    httpGet(url,'json',false,function(){
        print("Board restart");
        boardModified = false;
        disableEndMoveButton();
    })
}

function endPlayerMove(){
    postData = JSON.stringify({'board': board, 'players': players})
    let url = '/end-move';
    httpPost(url,'json',postData,function(data){
        console.log('Board valid? ' +data.valid)
        if(data.valid == "true"){
            disableEndMoveButton();
        }else{
            displayMessage(data.message, 3000);
        }
        boardModified = false;
    })
}


function keyPressed(){
    if( keyCode == 32){
        board.push('')
    }
}

function mousePressed(){
    if(mouseX<0 || mouseX>width || mouseY<0 || mouseY>height)return;

    selectedTile = createVector(floor(mouseX/sizeX), floor(mouseY/sizeY));
    if(selectedTile.x <0 || selectedTile.x>COLS || selectedTile.y <0 || selectedTile.y>ROWS ){
        selectedTile = createVector(-1,-1)
    }
    boardModified = true;
}

function mouseReleased(){
    if(mouseX<0 || mouseX>width || mouseY<0 || mouseY>height)return;

  let newTileLocation = createVector(floor(mouseX/sizeX),floor(mouseY/sizeY))
  if(newTileLocation.y>=ROWS){ //Moved to player tileset
    let index = (newTileLocation.y-ROWS)*COLS+newTileLocation.x;
    let tileValue;

    //Moved from player tileset (cannot move from board as to satisfy table contraint)
    if(selectedTile.y>=ROWS){
      tileValue = players[selectedPlayer][(selectedTile.y-ROWS)*COLS+selectedTile.x]
      players[selectedPlayer].splice((selectedTile.y-ROWS)*COLS+selectedTile.x,1) //Remove from player's tileset
      players[selectedPlayer].splice(index,0,tileValue); //Add to player tileset
    }
  }else{
    let index = newTileLocation.y*COLS+newTileLocation.x;
    let tileValue;

    //Moved from player tileset
    if(selectedTile.y>=ROWS){
      tileValue = players[selectedPlayer][selectedTile.y-ROWS+selectedTile.x]
      players[selectedPlayer].splice(selectedTile.y-ROWS+selectedTile.x,1) //Remove from player's tileset

    // Moved from board tileset
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


function disableEndMoveButton(){
    endMoveButton.addClass('disabled');
}