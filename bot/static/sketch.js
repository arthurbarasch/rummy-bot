

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
  stroke('#bbbbbb')
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

  displayPlayerTurnIndicator();
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
  buttons = []
  endMoveButton = createButton('END MOVE');
  endMoveButton.mousePressed(endPlayerMove);
  endMoveButton.addClass('disabled');
  buttons.push(endMoveButton)

  restartButton = createButton('NEW GAME (restart)');
  restartButton.addClass('btn-green')
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
        displayPlayerTurnIndicator(100)
    }

    players = state.players;
    updateBoardScore();
}

var turnIndicatorPhase = 0
function displayPlayerTurnIndicator(ms){
    let interval;
    if(!ms && turnIndicatorPhase>0){
        turnIndicatorPhase--;
        rect(width/2, height/2, 300,90)
        text("Player "+(selectedPlayer+1)+",\nit's your turn", width/2, height/2)
    }else if(ms > 0){
        turnIndicatorPhase = ms
    }
}

function displayPlayerTiles(){
    push();
    translate(sizeX/2, sizeY/2)
    let imagePointer = createVector(0,ROWS);
    for(let tile of players[selectedPlayer]){
        if(imagePointer.x>=COLS){
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
