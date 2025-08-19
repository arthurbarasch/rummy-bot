

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
var drawPileSize = 0;
var selectedPlayer = 0;
var selectedTile = undefined;
var boardModified = false;


//Buttons
var buttons = [];

function setup() {
  let cnv = createCanvas(windowWidth*0.55, 550);
  cnv.parent('canvas-container')
  createControlButtons();
  textAlign(CENTER);
  rectMode(CENTER);
  textSize(24);
  stroke('#bbbbbb')

    for(let i=0; i<COLS;i++){
        board.push([])
        for(let j=0;j<ROWS;j++){
            board[i].push(false);
        }
    }
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
  text('Max score: '+currMaxScore,80, height-PLAYER_ROWS*sizeY-10)
  text('Score on the board: '+boardScore,125, height-PLAYER_ROWS*sizeY-50)
  pop();

  // Display tiles
  if(solution){
    displaySolution()
  }else{
    displayBoardTiles();
  }
  displayPlayerTiles();
  displayMessages();
  displayMouseTileSlot();
}

function displayMouseTileSlot(){
    if(selectedTile){
      push();
      translate(floor(mouseX/sizeX)*sizeX, floor(mouseY/sizeY)*sizeY);
      translate(sizeX/2,sizeY/2)
      fill(205,50)
      rect(0,0, sizeX, sizeY, 10);
      pop();
    }
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
    for(let i=0; i<COLS;i++){
        for(let j=0;j<ROWS;j++){
            boardScore += board[j][i]?board[j][i][1]:0;
        }
    }
}

function createControlButtons(){
  buttons = []
  let drawTileButton = createButton('Draw tile');
  drawTileButton.mousePressed(drawRandomTile);
  buttons.push(drawTileButton)

  endMoveButton = createButton('END MOVE');
  endMoveButton.mousePressed(endPlayerMove);
  endMoveButton.addClass('disabled');
  buttons.push(endMoveButton)

  let restartButton = createButton('NEW GAME (HUMAN vs AI)');
  restartButton.addClass('btn-green')
  restartButton.mousePressed(newGame);
  buttons.push(restartButton);

  let restartButtonAI = createButton('NEW GAME (AI vs AI)');
  restartButtonAI.addClass('btn-green')
  restartButtonAI.mousePressed(newGameAI);
  buttons.push(restartButtonAI)

  let solveButton = createButton('SOLVE');
  solveButton.mousePressed(solveTable);
  buttons.push(solveButton)

  let otherSolutionsButton = createButton('OTHER SOLUTIONS');
  otherSolutionsButton.mousePressed(calculateOtherSolutions);
  buttons.push(otherSolutionsButton)

//  roiButton = createButton('Select Region of Interest (ROI)');
//  roiButton.mousePressed(selectRoi);
//  buttons.push(roiButton)

  for(let b of buttons){
    b.parent('controls');
    b.addClass('btn m-1')
    b.mouseClicked(function(){
        solution = null;
    })
  }
}

var messages = [];
function displayMessage(message,ms){
    messages.push([message, Date.now()+ms])
}

function displayMessages(){
    if(messages.length>0){
        if(messages[0][1]>Date.now()){
            rect(width/2, height/2, 400+10*messages[0][0].length,90);
            text(messages[0][0], width/2, height/2);
        }else{
            messages.splice(0,1);
        }
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

function displayBoardTiles(){
  push();
  translate(sizeX/2,sizeY/2)
  for(let i=0; i<COLS;i++){
    for(let j=0;j<ROWS;j++){
        if(board[j][i]){
            drawTile(board[j][i],createVector(i,j))
        }
    }
  }
  pop();
}

function drawTile(tile,pos){
    push();
    if(!tile){
        translate(pos.x*sizeX, pos.y*sizeY);
        fill(205,50);
        rect(0,0, sizeX, sizeY, 10);
        pop();
        return;
    }

    if(mouseX>pos.x*sizeX && mouseX<(pos.x+1)*sizeX &&
        mouseY>pos.y*sizeY && mouseY<(pos.y+1)*sizeY){

        if(selectedTile){
          push();
          translate(pos.x*sizeX, pos.y*sizeY);
          fill(205,50)
          rect(0,0, sizeX, sizeY, 10);
          pop();
        }
        strokeWeight(3);
    }else if(selectedTile && selectedTile.x==pos.x && selectedTile.y==pos.y){
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
    }
    pop();
}
