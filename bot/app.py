#https://towardsdatascience.com/video-streaming-in-web-browsers-with-opencv-flask-93a38846fe00

#Import necessary libraries
from flask import Flask, render_template, Response, request
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

#Initialize the Flask app
app = Flask(__name__)

#The program will detect text every 40 frames
FRAME_INTERVAL = 40

#Rummy model
controller = None
rummyBotSolutions = []
currSolutionIndex = -1

class RummyDetector:
    def __init__(self):
        self.cannyThreshold = 100
        self.initTesseract()
        self.frameNr = 0
        self.roi = 0
        self.img = 0


    # Set the tesseract executable file
    def initTesseract(self):
        tess.pytesseract.tesseract_cmd =  'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    def setCanny(self,canny):
        self.cannyThreshold = canny

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




rd = RummyDetector()

@app.route('/', methods=['POST', 'GET'])
def index():
    global controller
    if request.method == "POST":
        req = request.form.get("canny")
        if req:
            rd.setCanny(int(req))
    controller = runRummyGame(solve=False)
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(rd.genFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/game-state', methods=['POST','GET'])
def sendGameState():
    global controller
    global currSolutionIndex
    global rummyBotSolutions

    if controller and controller.model:
        if currSolutionIndex>=0 and currSolutionIndex<len(rummyBotSolutions):
            return rummyBotSolutions[currSolutionIndex].encodeJSON()
        return controller.model.encodeJSON()
    else:
        return {}

@app.route('/end-move', methods=['POST','GET'])
def endMove():
    global controller
    prev = RummyModel(controller.model)
    valid = controller.model.decodeJSON(request.data)
    print('Player ended move. Board is{} valid'.format(' ' if valid else ' not'))
    message = ''
    if valid:
        if controller.model.getCurrentPlayer().quarantine and prev.getBoardScore()+30 > controller.model.getBoardScore():
            message = 'You need to place 30 points down in one round to exit quarantine'
            controller.init(prev)
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
    controller.model.restart()
    controller.model.start()
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
    currSolutionIndex +=1
    if currSolutionIndex>=len(rummyBotSolutions):
        currSolutionIndex=-1
    else:
        print(len(rummyBotSolutions))
        Timer(2, nextSolution).start()

@app.route('/solve', methods=['POST','GET'])
def solve():
    global controller, rummyBotSolutions
    solver = RummySolver(controller.model)
    score = solver.maxScore()
    return {'score':score, 'solution': solver.solution.encodeJSON()}

@app.route('/select-roi', methods=['POST','GET'])
def selectROI():
    rd.selectROI()
    return {}

def startLocalServer():
    app.run(debug=False)