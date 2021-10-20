var board = [];
var players = [['B10','B11','B12'],['A4','D4','B4']];
var selectedPlayer = 0;
var selectedTile;
var boardModified = false;

//Board dimensions
var ROWS = 6;
var COLS = 18;
var PLAYER_ROWS = 2;
var sizeX=0;
var sizeY=0;

//Game
var suits = ['black','blue', '#f5b800', 'red']; //Colors for each of the suits

var svgs = [];
var test;

//Buttons
var endMoveButton;

function setup() {
  let cnv = createCanvas(windowWidth*0.5, 600);

  endMoveButton = createButton('END MOVE');
  endMoveButton.mousePressed(endPlayerMove);
//  endMoveButton.addClass("disabled");

  board = new Array();
  selectedTile = createVector(-1,-1);
  textAlign(CENTER);
  rectMode(CENTER);
  textSize(24);
  cnv.addClass('canvas');
}

function draw() {
  background(230);
  updateGameState();
  sizeX = width/COLS;
  sizeY = height/(ROWS+PLAYER_ROWS);

  // Player stand
  push();
  fill('green')
  rect(width/2,(ROWS+1)*sizeY,width,PLAYER_ROWS*sizeY)
  pop();

  // Display tiles
  translate(sizeX/2, sizeY/2)
  displayPlayerTiles();
  displayBoardTiles();
}

function updateGameState(){
    if(frameCount%60==10 && !boardModified){
        let url = '/game-state';
        httpGet(url,'json',false,setGameState)
    }
}

function setGameState(state){
    board = [];
    if(!state.board.runs) return

    for(let run of state.board.runs){
        board.push(...run)
        board.push('')
    }

    for(let group of state.board.groups){
        board.push(...group)
        board.push('')
    }
    players = state.players
}

function displayPlayerTiles(){
    let imagePointer = createVector(0,ROWS);
    for(let tile of players[selectedPlayer]){
        if(imagePointer.x>COLS){
          imagePointer.x = 0
          imagePointer.y++;
        }
        drawTile(tile, imagePointer);
        imagePointer.x++;
    }
}

var currentGroupLength = 0;
function displayBoardTiles(){
  let imagePointer = createVector(0,0);
  for(let i=0;i<board.length;i++){
    if(board[i]!=''){
       drawTile(board[i],imagePointer);
    }else{
        let nextSpace=i;
        while((board[nextSpace]!='' && nextSpace+1<board.length) || nextSpace != i){
            nextSpace++;
        }
        currentGroupLength = nextSpace-i;
        if(imagePointer.x+currentGroupLength>COLS){
            imagePointer.x = 0
            imagePointer.y++;
        }
    }
    imagePointer.x++;
  }
}

function drawTile(tile,pos){
    push();
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
    print(board)
    if(tile[0]+tile[1]>0){
        fill(suits[tile[0]-1])
        noStroke();
        text(tile[1],0,0);
    }else{
        text('J',0,0);
    }
    pop();
}

function mousePressed(){
  endMoveButton.removeClass('disabled');
  selectedTile = createVector(floor(mouseX/sizeX), floor(mouseY/sizeY)) ;
}

function endPlayerMove(){
    boardModified = false;
    endMoveButton.addClass('disabled');

    let url = '/end-move';
    httpGet(url,'json',false,setGameState)
    print("End move")
}


function mouseReleased(){
  let newTileLocation = createVector(floor(mouseX/sizeX),floor(mouseY/sizeY))
  if(newTileLocation.y>=ROWS){ //Moved to player tileset

  }else{
    let index = newTileLocation.y*COLS+newTileLocation.x;
    let tileValue;
    if(selectedTile.y>=ROWS){//Moved from player tileset
      tileValue = players[selectedPlayer][selectedTile.y-ROWS+selectedTile.x]
      players[selectedPlayer].splice(selectedTile.y-ROWS+selectedTile.x,1) //Remove from player's tileset
    }else{
      tileValue = board[selectedTile.y*COLS+selectedTile.x]
      board.splice(selectedTile.y*COLS+selectedTile.x,1) //Remove from board tileset
    }
    boardModified = true;
    board.splice(index,0,tileValue); //Add to board tileset
  }
  selectedTile = createVector(-1,-1);
}