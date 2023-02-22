#https://towardsdatascience.com/video-streaming-in-web-browsers-with-opencv-flask-93a38846fe00

#Import necessary libraries
from flask import Flask, render_template, Response, request, jsonify
from threading import Timer
# import cv2
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.io import loadmat
import pytesseract as tess
from bot.controller import runRummyGame
from bot.solver import RummySolver
from bot.model import RummyModel
import logging

#Initialize the Flask app
app = Flask(__name__)

#The program will detect text every 40 frames
FRAME_INTERVAL = 40

#Rummy model
controller = None
rummyBotSolutions = []
currSolutionIndex = -1


# class RummyApp:
#     def __init__(self):
#


    # def genFrames(self):
    #     while True:
    #         self.frameNr += 1
    #         success, self.img = camera.read()  # read the camera frame
    #         if not success:
    #             break
    #         else:
    #             img = self.detectEdges(self.img)
    #             #img = self.detectDigits(frame)
    #
    #             # Crop selected roi from raw image
    #             if self.roi!=0:
    #                 img = img[int(self.roi[1]):int(self.roi[1] + self.roi[3]), int(self.roi[0]):int(self.roi[0] + self.roi[2])]
    #             frame = img.tobytes()
    #             yield (b'--frame\r\n'
    #                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
    #


@app.route('/', methods=['POST', 'GET'])
def index():
    global controller

    return render_template('index.html')

@app.route('/game-state', methods=['POST','GET'])
def sendGameState():
    global controller
    global currSolutionIndex
    global rummyBotSolutions

    if controller and controller.model:
        return jsonifyModel()
    else:
        return {}

@app.route('/end-move', methods=['POST', 'GET'])
def endMove():
    global controller
    prev = RummyModel(controller.model)
    logging.info('Move ended. Server received:{}'.format(str(request.data)))
    valid = controller.model.decodeJSON(request.data, app)
    print('Player ended move. Board is{} valid'.format(' ' if valid else ' not'))
    message = ''
    if valid:
        if controller.model.getCurrentPlayer().quarantine and controller.model.getBoardScore()-prev.getBoardScore() < 30:
            message = 'You need to place 30 points down in one round to exit quarantine'
            controller.init(prev)
        elif len(controller.model.getBoardTilePool()) == len(prev.getBoardTilePool()):
            message = 'Cannot end move without placing any tiles'
            controller.init(prev)
        elif controller.checkWinCondition() is not False:
            message = 'GAME OVER! Player {} won!'.format(controller.checkWinCondition()+1)
        else:
            controller.model.getCurrentPlayer().quarantine = False
            Timer(1.0, controller.nextPlayer).start()
            message = 'Next player'
    else:
        message = 'Cannot end move, the board is not valid. Returning tiles'
        controller.init(prev)
    return {'valid': valid, 'message': message}

@app.route('/restart', methods=['POST','GET'])
def restart():
    global controller
    global currSolutionIndex
    controller = runRummyGame(solve=False)
    currSolutionIndex = -1
    return {}

@app.route('/other-solutions', methods=['POST','GET'])
def otherSolutions():
    global controller
    solver = RummySolver(controller.model)
    solver.maxScore()
    return jsonify(solutions=solver.otherSolutions)

@app.route('/restart-ai', methods=['POST','GET'])
def restartAI():
    global controller
    global currSolutionIndex
    controller = runRummyGame(solve=False,game_mode=1)
    currSolutionIndex = -1
    return {}

@app.route('/add-hand', methods=['POST','GET'])
def addRandomHand():
    global controller
    controller.model.addRandomHand()
    return {}

@app.route('/draw-tile', methods=['POST','GET'])
def drawTile():
    global controller
    controller.model.drawTile(controller.model.playerTurn)
    Timer(1.0,controller.nextPlayer).start()
    return {}

def nextSolution():
    global currSolutionIndex, rummyBotSolutions
    currSolutionIndex += 1
    if currSolutionIndex >= len(rummyBotSolutions):
        currSolutionIndex = -1
    else:
        print(len(rummyBotSolutions))
        Timer(2, nextSolution).start()

@app.route('/solve', methods=['POST','GET'])
def solve():
    global controller, rummyBotSolutions
    solver = RummySolver(controller.model)
    score = solver.maxScore()
    return jsonifySolution(score,solver.solution,solver.score)

def startLocalServer():
    app.run(debug=False)


def jsonifyModel():
    global controller
    model = controller.model
    return jsonify(
        board=model.getBoardAsArray(),
        players=[p.tiles for p in model.players],
        playerTurn=model.playerTurn,
        drawPileSize=len(model.drawPile)
    )

def jsonifySolution(score,solution,scoreArray):
    arr = []
    for valArray in scoreArray:
        arr.append([])
        for scores in valArray.values():
            arr[-1].append((scores[0] if scores[0] >= 0 else -999, scores[1].getBoardAsArray()))

    return jsonify(
        score=score if score > 0 else -999,
        board=solution.getBoardAsArray(),
        players=[p.tiles for p in solution.players],
        playerTurn=solution.playerTurn,
        drawPileSize=len(solution.drawPile),
        scoreArray=arr
    )