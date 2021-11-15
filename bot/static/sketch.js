

//Board dimensions
var ROWS = 6;
var COLS = 18;
var PLAYER_ROWS = 2;
var sizeX=0;
var sizeY=0;

//Game
               //1 2 3 4
var suits = ['black','blue', '#f5b800', 'red']; //Colors for each of the suits
var playerColors = ['#a3fc88','#80587a','#34707d','#e0a243'];
var test;
var currMaxScore = 0;
var boardScore = 0;
var solution;

var board = [];
var players = [[],[]];
var selectedPlayer = 0;
var selectedTile;
var boardModified = false;


//Buttons
var buttons = [];

function setup() {
  let cnv = createCanvas(windowWidth*0.55, 550);
  cnv.parent('canvas-container')
  createControlButtons();

  board = new Array();
  selectedTile = createVector(-1,-1);
  textAlign(CENTER);
  rectMode(CENTER);
  textSize(24);
}

function draw() {
  background(230);
  updateGameState();
  sizeX = width/COLS;
  sizeY = height/(ROWS+PLAYER_ROWS);

  // Player stand
  push();
  fill(playerColors[selectedPlayer])
  rect(width/2,(ROWS+1)*sizeY,width,PLAYER_ROWS*sizeY)
  fill(0)

  text('Player '+(selectedPlayer+1),width-50, height-PLAYER_ROWS*sizeY-10)
  text('Max score (RummyBot): '+currMaxScore,150, height-PLAYER_ROWS*sizeY-10)
  text('Score on the board: '+boardScore,125, height-PLAYER_ROWS*sizeY-50)
  pop();

  // Display tiles
  if(solution){
    displaySolution()
  }else{
    displayBoardTiles();
  }
  displayPlayerTiles();
}

function displaySolution(){
    setGameState(solution)
    push();
    noStroke();
    fill('red')
    text("SOLUTION", width-90, height-PLAYER_ROWS*sizeY-75)
    fill(255,0,0, 50)
    rect(width/2,height/2,width,height)
    pop();
    displayBoardTiles();
}

function updateBoardScore(){
    boardScore = 0
    for(let tile of board){
        if(tile != ''){
            boardScore+=tile[1]
        }
    }
}

function createControlButtons(){
  endMoveButton = createButton('END MOVE');
  endMoveButton.mousePressed(endPlayerMove);
  endMoveButton.addClass('disabled');
  buttons.push(endMoveButton)

  restartButton = createButton('Restart');
  restartButton.mousePressed(restartBoard);
  buttons.push(restartButton)

  randomButton = createButton('Add random hand');
  randomButton.mousePressed(addRandomHand);
  buttons.push(randomButton)

  drawTileButton = createButton('Draw tile');
  drawTileButton.mousePressed(drawRandomTile);
  buttons.push(drawTileButton)

  solveButton = createButton('SOLVE');
  solveButton.mousePressed(solveTable);
  buttons.push(solveButton)

  roiButton = createButton('Select Region of Interest (ROI)');
  roiButton.mousePressed(selectRoi);
  buttons.push(roiButton)

  for(let b of buttons){
    b.parent('controls');
    b.addClass('btn m-1')
    b.mouseClicked(function(){
        solution = null;
    })
  }
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

function updateGameState(){
    if(frameCount%20==1 && !boardModified && !solution){
        let url = '/game-state';
        httpGet(url,'json',false,setGameState)
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
    selectedPlayer = state.playerTurn;
    players = state.players;
    updateBoardScore();
}

function displayPlayerTiles(){
    push();
    translate(sizeX/2, sizeY/2)
    let imagePointer = createVector(0,ROWS);
    for(let tile of players[selectedPlayer]){
        if(imagePointer.x>COLS){
          imagePointer.x = 0
          imagePointer.y++;
        }
        drawTile(tile, imagePointer);
        imagePointer.x++;
    }
    pop();
}

var currentGroupLength = 0;
function displayBoardTiles(){
  push();
  translate(sizeX/2, sizeY/2)
  let imagePointer = createVector(0,0);
  for(let i=0;i<board.length;i++){
    if(keyCode == 32 && i == board.length-1){
        drawTile('', imagePointer)
    }

    if(board[i]!=''){
       drawTile(board[i],imagePointer);
    }else{
        let nextSpace=i;
        while((board[nextSpace]!='' && nextSpace+1<=board.length) || nextSpace == i){
            nextSpace++;
        }
        currentGroupLength = nextSpace-i;
        if(imagePointer.x+currentGroupLength>COLS){
            imagePointer.x = 0
            imagePointer.y++;
            continue;
        }
    }
    imagePointer.x++;
  }
  pop();
}

function drawTile(tile,pos){
    push();
    if(tile==''){
        translate(pos.x*sizeX, pos.y*sizeY);
        fill(205,50)
        rect(0,0, sizeX, sizeY, 10);
        pop()
        return;
    }

    if(mouseX>pos.x*sizeX && mouseX<(pos.x+1)*sizeX &&
        mouseY>pos.y*sizeY && mouseY<(pos.y+1)*sizeY){

        if(selectedTile.x>=0){
          push();
          translate(pos.x*sizeX, pos.y*sizeY);
          fill(205,50)
          rect(0,0, sizeX, sizeY, 10);
          pop();
          pos.x++;
        }
        strokeWeight(3);
    }else if(selectedTile.x==pos.x && selectedTile.y==pos.y){
        strokeWeight(3);
        stroke('red');
    }else{
        strokeWeight(1);
    }
    translate(pos.x*sizeX, pos.y*sizeY);
    rect(0,0, sizeX, sizeY, 10);
    if(tile[0]+tile[1]>0){
        fill(suits[tile[0]-1])
        noStroke();
        text(tile[1],0,0);
    }else{
        text('J',0,0);
    }
    pop();
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

function endPlayerMove(){
    boardModified = false;
    endMoveButton.addClass('disabled');
    postData = JSON.stringify({board, players})
    let url = '/end-move';
    httpPost(url,'json',false,function(data){

    })
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