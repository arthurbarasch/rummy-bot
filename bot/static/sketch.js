

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
var selectedTile;
var boardModified = false;
var gameOver = false;


//Buttons
var buttons = [];
var drawTileButton; // For updating the display text to show draw pile size

function setup() {

  let cnv = createCanvas(document.getElementById('canvas-container').clientWidth, 550);
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
  displayMessages();
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
        if(tile && tile != ''){
            boardScore+=tile[1]
        }
    }
}

function createControlButtons(){
  buttons = []

  restartButton = createButton('NEW GAME<br><h5>HUMAN vs. AI</h5>');
  restartButton.addClass('btn-green')
  restartButton.mousePressed(function(){newGame("HUMAN vs. AI")});
  buttons.push(restartButton)

  botvbotButton = createButton('NEW GAME<br><h5>AI vs. AI</h5>');
  botvbotButton.addClass('btn-green')
  botvbotButton.mousePressed(function(){newGame("AI vs. AI")});
  buttons.push(botvbotButton)

  drawTileButton = createButton('Draw tile');
  drawTileButton.mousePressed(drawRandomTile);
  buttons.push(drawTileButton)

  endMoveButton = createButton('END MOVE');
  endMoveButton.mousePressed(endPlayerMove);
  endMoveButton.addClass('disabled');
  buttons.push(endMoveButton)

  randomButton = createButton('Add random hand');
  randomButton.mousePressed(addRandomHand);
  buttons.push(randomButton)

  solveButton = createButton('SOLVE');
  solveButton.mousePressed(solveTable);
  buttons.push(solveButton)

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
    if(!tile || tile==''){
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
