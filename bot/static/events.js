function httpGetError(){
    console.log('ERROR: on http GET')
}

function updateGameState(){
    if(frameCount%30==1 && !boardModified && !solution){
        let url = '/game-state';
        httpGet(url,'json',false,setGameState, httpGetError);
    }
}

function setGameState(state){
    if(!state || !state.board) return
    // for(let run of state.board.runs){
    //     board.push(...run)
    //     board.push('')
    // }
    //
    // for(let group of state.board.groups){
    //     board.push(...group)
    //     board.push('')
    // }
    let arr = [];

    for(let g of state.board){
        if((arr.length%COLS)+g.length >= COLS){
            let n = COLS-(arr.length%COLS)
            while(n>0){
                arr.push(false);
                n--;
            }
        }

        arr.push(...g)
        arr.push(false)
    }

    for(let i=0; i<COLS;i++){
        for(let j=0;j<ROWS;j++){
            if(j*COLS+i>= arr.length) {
                board[j][i] = false;
                continue;
            }

            board[j][i] = arr[j*COLS+i]
        }
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
        print('NEXT SOLUTION')
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
    postData = JSON.stringify({'board': collectBoardAsArray(), 'players': players})
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

function collectBoardAsArray(){
    let arr = []
    let space = true
    for(let i=0;i<COLS*ROWS;i++){
        let val = board[floor(i/COLS)][i%COLS];
        if(val){
            arr.push(val);
            space = false;
        }else if(!space){
            space = true
            arr.push('')
        }
    }
    return arr;
}

function mousePressed(){
    if(mouseX<0 || mouseX>width || mouseY<0 || mouseY>height)return;

    if(selectedTile){
        boardModified = true;

        newLocation = createVector(floor(mouseX/sizeX), floor(mouseY/sizeY));

        if(newLocation.y>=ROWS)return;

        if(selectedTile.y>=ROWS){
            //Moved from player tileset
            let tile = players[selectedPlayer][(selectedTile.y-ROWS)*COLS+selectedTile.x];
            board[newLocation.y][newLocation.x] = tile?tile.slice():false;
            players[selectedPlayer][(selectedTile.y-ROWS)*COLS+selectedTile.x] = false;

        }else{
            //Moved from board
            temp = board[newLocation.y][newLocation.x]?board[newLocation.y][newLocation.x].slice():false;
            board[newLocation.y][newLocation.x] = board[selectedTile.y][selectedTile.x]?board[selectedTile.y][selectedTile.x].slice():false;
            board[selectedTile.y][selectedTile.x] = temp;
        }
        enableEndMoveButton();
        selectedTile = undefined;

        updateBoardScore()
        return;
    }


    selectedTile = createVector(floor(mouseX/sizeX), floor(mouseY/sizeY));
    if(selectedTile.x <0 || selectedTile.x>COLS || selectedTile.y <0 || selectedTile.y>ROWS ){
        selectedTile = createVector(-1,-1)
    }
}
//
// function mouseReleased(){
//     if(mouseX<0 || mouseX>width || mouseY<0 || mouseY>height)return;
//
//   let newTileLocation = createVector(floor(mouseX/sizeX),floor(mouseY/sizeY))
//   if(newTileLocation.y>=ROWS){ //Moved to player tileset
//     let index = (newTileLocation.y-ROWS)*COLS+newTileLocation.x;
//     let tileValue;
//
//     //Moved from player tileset (cannot move from board as to satisfy table contraint)
//     if(selectedTile.y>=ROWS){
//       tileValue = players[selectedPlayer][(selectedTile.y-ROWS)*COLS+selectedTile.x]
//       players[selectedPlayer].splice((selectedTile.y-ROWS)*COLS+selectedTile.x,1) //Remove from player's tileset
//       players[selectedPlayer].splice(index,0,tileValue); //Add to player tileset
//     }
//   }else{
//     let index = newTileLocation.y*COLS+newTileLocation.x;
//     let tileValue;
//
//     //Moved from player tileset
//     if(selectedTile.y>=ROWS){
//       tileValue = players[selectedPlayer][selectedTile.y-ROWS+selectedTile.x]
//       players[selectedPlayer].splice(selectedTile.y-ROWS+selectedTile.x,1) //Remove from player's tileset
//
//     // Moved from board tileset
//     }else{
//       tileValue = board[selectedTile.y*COLS+selectedTile.x]
//       board.splice(selectedTile.y*COLS+selectedTile.x,1) //Remove from board tileset
//     }
//     endMoveButton.removeClass('disabled');
//     board.splice(index,0,tileValue); //Add to board tileset
//   }
//   selectedTile = createVector(-1,-1);
//   updateBoardScore();
// }


function disableEndMoveButton(){
    endMoveButton.addClass('disabled');
}

function enableEndMoveButton(){
    endMoveButton.removeClass('disabled');
}