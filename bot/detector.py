#https://towardsdatascience.com/video-streaming-in-web-browsers-with-opencv-flask-93a38846fe00

#Import necessary libraries
from flask import Flask, render_template, Response, request
from threading import Timer
import cv2
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
camera = cv2.VideoCapture(0)

#Rummy model
model,view,controller = None,None,None
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

    def genFrames(self):
        while True:
            self.frameNr += 1
            success, self.img = camera.read()  # read the camera frame
            if not success:
                break
            else:
                img = self.detectEdges(self.img)
                #img = self.detectDigits(frame)

                # Crop selected roi from raw image
                if self.roi!=0:
                    img = img[int(self.roi[1]):int(self.roi[1] + self.roi[3]), int(self.roi[0]):int(self.roi[0] + self.roi[2])]
                frame = img.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


    def detectDigits(self, img):
        if(self.frameNr>=FRAME_INTERVAL):
            self.frameNr=0
            temp = tess.pytesseract.image_to_string(img)
            if len(temp)>1:
                print(temp)

        ret, img = cv2.imencode('.png', img)
        return img

    def detectEdges(self,img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(gray, (3, 3), 0)
        canny = cv2.Canny(img_blur, self.cannyThreshold, self.cannyThreshold+40)  # apply canny to roi

        # Find contours
        contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Draw contours
        drawing = np.zeros((canny.shape[0], canny.shape[1], 3), dtype=np.uint8)
        for i in range(len(contours)):
            cv2.drawContours(drawing, contours, i, (240,100,60), 1, cv2.LINE_8, hierarchy, 0)

        ret, newImg = cv2.imencode('.jpg', drawing)
        return newImg

    def selectROI(self):
        self.roi = cv2.selectROI(self.img)

rd = RummyDetector()

@app.route('/', methods=['POST', 'GET'])
def index():
    global model,view,controller
    if request.method == "POST":
        req = request.form.get("canny")
        if req:
            rd.setCanny(int(req))
    model, view, controller = runRummyGame(solve=False)
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(rd.genFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/game-state', methods=['POST','GET'])
def sendGameState():
    global model
    global currSolutionIndex
    global rummyBotSolutions

    if model:
        if currSolutionIndex>=0 and currSolutionIndex<len(rummyBotSolutions):
            return rummyBotSolutions[currSolutionIndex].encodeJSON()
        return model.encodeJSON()
    else:
        return {}

@app.route('/end-move', methods=['POST','GET'])
def endMove():
    global model, controller
    prev = RummyModel(model)
    model.board["runs"] = []
    model.board["groups"] = []
    valid = model.decodeJSON(request.data)
    print('Validity {}'.format(valid))
    if valid:
        Timer(1.0, controller.nextPlayer).start()
    else:
        model = prev
    return {'valid': valid}

@app.route('/restart', methods=['POST','GET'])
def restart():
    global model
    global currSolutionIndex
    model.restart()
    model.start()
    currSolutionIndex = -1
    return {}

@app.route('/add-hand', methods=['POST','GET'])
def addRandomHand():
    global model
    model.addRandomHand()
    return {}

@app.route('/draw-tile', methods=['POST','GET'])
def drawTile():
    global model, controller
    model.drawTile(model.playerTurn)
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
    global model, rummyBotSolutions
    solver = RummySolver(model)
    score,solution = solver.maxScore()
    print(solution.encodeJSON())
    return {'score':score, 'solution': solution.encodeJSON()}

@app.route('/select-roi', methods=['POST','GET'])
def selectROI():
    global model
    rd.selectROI()
    return {}

def startLocalServer():
    app.run(debug=False)