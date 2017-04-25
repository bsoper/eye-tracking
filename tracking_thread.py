from PyQt5 import QtCore as QtCore
from PyQt5 import QtWidgets as QtWidgets
from PyQt5 import QtGui as QtGu
from PyQt5.QtCore import *
import sys
import cv2
import collections
import math
import pyautogui

class TrackingThread(QtCore.QThread):

    request_button_centers = pyqtSignal()
    move_cursor_to_button = pyqtSignal(tuple)

    def __init__(self, parent=None):
        """
        Initializes tracking thread - a child of QThread to be used in
        conjunction with the ui_widget
        """
        super(TrackingThread, self).__init__(parent)

        #Values required to run thread
        self.found_face = False
        self.mutex = QtCore.QMutex()
        self.condition = QtCore.QWaitCondition()
        self.restart = False
        self.abort = False
        self.loop_count = 0

        #Centers of buttons used for snapping
        self.button_centers = []

        #Connect signal to update buttons to setButtonCenters
        self.center = None
        self.pupil_avg = None

        pyautogui.FAILSAFE = False
        self.screen_x, self.screen_y = pyautogui.size()
        self.prev_pos = (0,0)
        self.num_new_pos = 0

        # Camera and screen parameters
        self.cam_x = 1920
        self.cam_y = 1080

    def __del__(self):
        """
        Deletes the thread when destruction is required
        """
        self.mutex.lock()
        self.abort = True
        self.condition.wakeOne()
        self.mutex.unlock()

        self.wait()

    @pyqtSlot(list)
    def setButtonCenters(self, centers):
        """
        Qt Signal to set button centers list based off of centers passed
        by signal emitter

        :param centers: The list of button centers
        :type centers: list[tuple(float,float)]
        """
        self.button_centers = centers

    @pyqtSlot()
    def calibrate(self):
        """
        Qt Slotted function to calibrate tracking mechanism based off of user
        eye position
        """
        # The multiplier used in the scaling factors are fairly arbitrary. This
        # gave us good results, but is something that should be available for
        # the user to change.
        self.center = self.pupil_avg
        self.x_scale_factor = math.floor(30000 / self.w) # 18600
        self.y_scale_factor = math.floor(30000 / self.w)

    def startProcessing(self):
        """
        Function called when this thread begins
        """
        locker = QtCore.QMutexLocker(self.mutex)

        if not self.isRunning():
            self.start(QtCore.QThread.LowPriority)
        else:
            self.restart = True
            self.condition.wakeOne()

    def findClosestCenter(self, cursor_pos):
        """
        Finds the closest button center to the current mouse position

        :param cursor_pos: The x,y position of the mouse cursor
        :type cursor_pos: tuple (float,float)
        """
        magnitude_vectors = []
        #Calculate vector between eye cursor and each button
        for center in self.button_centers:
            b_x = center[0]
            b_y = center[1]
            c_x = cursor_pos[0]
            c_y = cursor_pos[1] + 100

            delta_x = abs(c_x - b_x)/1000
            delta_y = abs(c_y - b_y)/1000

            mag = math.sqrt((math.pow(2,delta_x) + math.pow(2,delta_y)))
            entry = (mag, center)
            magnitude_vectors.append(entry)


        #See which one is closest
        closest_entry = magnitude_vectors[0]
        for entry in magnitude_vectors:
            if(entry[0] < closest_entry[0]):
                closest_entry = entry

        # Adjust cursor so it is not on text
        position = (closest_entry[1][0], closest_entry[1][1] + 30)
        if position == self.prev_pos:
            return
        elif self.num_new_pos < 3:
            self.num_new_pos += 1
        else:
            self.prev_pos = position
            self.num_new_pos = 0

        #Move mouse to a the button position.
        pyautogui.moveTo(position[0], position[1], 0.2)

    def findEyeCenter(self,gray_eye, thresh_eye):
        """ Approximates the center of the pupil by selecting
            the darkest point in gray_eye that is within the blob detected in
            thresh_eye

            :param gray_eye: Gray-scale image of eye
            :param thresh_eye: binary eye image with contours filled in

            :return: The pixel location of pupil center
            :rtype: tuple(int,int)
        """
        dims = gray_eye.shape # get shape image
        minBlack = 300
        pupil = [0, 0]

        for i in range(dims[0]):
            for j in range(dims[1]):
                if thresh_eye[i][j]:
                    if gray_eye[i][j] < minBlack:
                        minBlack = gray_eye[i][j]
                        pupil[0] = i
                        pupil[1] = j

        return pupil

    def getPupilAvgFromFace(self,gray_face, eyes, x, y, w, h):
        """
        Takes a grey version of face image, a list of eyes, and the x, y, w, h,
        coordinates of the face. Returns a list [x, y] for the average between
        the eyes contained in the list.

        :param gray_face: A gray-scale version of the face image
        :param eyes: A list of eyes located within image
        :param x: The x coordinate of the face
        :param y: The y coordinate of the face
        :param w: The width of the face
        :param h: The height of the face

        :return: The average center position of the eyes in the list
        :rtype: tuple(int,int)
        """
        pupil_avg = [0,0]
        for (ex,ey,ew,eh) in eyes:
            gray_eye = gray_face[ey:ey+eh, ex:ex+ew] # get eye

            # apply gaussian blur to image
            blur = cv2.GaussianBlur(gray_eye, (15,15), 3*gray_eye.shape[0])
            retval, thresh = cv2.threshold(~blur, 150, 255, cv2.THRESH_BINARY)
            _,contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(thresh, contours, -1, (255, 255, 255), -1)
            pupil = self.findEyeCenter(gray_eye, thresh)

            pupil_avg[0] += pupil[1] + ex + x;
            pupil_avg[1] += pupil[0] + ey + y;

        # Compute pupil average
        pupil_avg = [x / len(eyes) for x in pupil_avg]

        return pupil_avg

    def scale_position(self, x, y):
        """
        Called to scale the position based on the resolution of the webcam.
        """
        x_scaled = 1.*x * self.screen_x / self.cam_x
        y_scaled = 1.*y * self.screen_y / self.cam_y
        return x_scaled, y_scaled

    def run(self):
        """
        Called when this thread begins to run. Image processing done within
        this function.
        """
        self.request_button_centers.emit()
        while True:
            face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
            left_eye_cascade = cv2.CascadeClassifier('haarcascade_lefteye_2splits.xml')
            right_eye_cascade = cv2.CascadeClassifier('haarcascade_righteye_2splits.xml')

            if face_cascade.empty():
                print("did not load face classifier.")

            if eye_cascade.empty():
                print("did not load eye classifier.")

            if left_eye_cascade.empty():
                print("did not load left eye classifier.")

            if right_eye_cascade.empty():
                print("did not load right eye classifier.")

            # The value passed to VideoCapture relates to the camera number for the OS
            cap = cv2.VideoCapture(0)
            
            rolling_pupil_avg = collections.deque(maxlen=3)
            blink_count = 0
            frame_count = 0

            while(True):
                # pull video frame
                ret, img = cap.read()
                img = cv2.flip(img,1)

                #Greyscale
                if(img.size == 0):
                    continue

                try:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                    # get faces
                    face_scale_factor = 1.3
                    face_min_neighbors = 3
                    (x,y,w,h) = face_cascade.detectMultiScale(img, face_scale_factor, face_min_neighbors)[0]
                    self.w = w
                except:
                    # If for some reason, you don't detect a face, try the next frame.
                    continue

                break

            self.found_face = True

            while(cap.isOpened()):
                # pull video frame
                ret, img = cap.read()
                img = cv2.flip(img,1)

                #Greyscale
                if(img.size == 0):
                    continue

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Pull face sub-image
                gray_face = gray[y:y+h, x:x+w]
                face = img[y:y+h, x:x+w]

                eyes = eye_cascade.detectMultiScale(gray_face, 3.0, 5) # locate eye regions
                left_eye = left_eye_cascade.detectMultiScale(gray_face, 3.0, 5) # locate left eye regions
                right_eye = right_eye_cascade.detectMultiScale(gray_face, 3.0, 5) # locate left eye regions

                # This ignores any frames where we have detected too few or too many eyes.
                # This generally won't filter out too many frames, as most detect eyes pretty well.
                # This is needed so we don't get bad data in our rolling averages.
                # Sometimes it will detect both eyes as right and left, so we just want to check if
                # it detected none, or more than two of each.
                if (len(left_eye) > 0 and len(left_eye) <= 2 and
                    len(right_eye) > 0 and len(right_eye) <= 2):
                    if len(eyes) == 0:
                        blink_count += 1
                        continue
                    elif len(eyes) == 2:
                        # Long blinks are not currently used, but this could be used.
                        # Blinks look for the number of frames where eyes are detected but not open eyes.
                        if blink_count >= 7:
                            pyautogui.click()
                            blink_count = 0
                        elif blink_count >= 2:
                            pyautogui.click()
                            blink_count = 0
                        else:
                            blink_count = 0

                # Ensure that two eyes have been detected.
                if len(eyes) != 2:
                    continue

                self.pupil_avg = self.getPupilAvgFromFace(gray_face, eyes, x, y, w, h)
                if self.center == None:
                    self.calibrate()

                x_scaled = self.center[0] + (self.pupil_avg[0] - self.center[0]) * self.x_scale_factor
                y_scaled = self.center[1] + (self.pupil_avg[1] - self.center[1]) * self.y_scale_factor

                rolling_pupil_avg.appendleft((x_scaled, y_scaled))

                avgs = (sum(a) for a in zip(*rolling_pupil_avg))
                avgs = [a / len(rolling_pupil_avg) for a in avgs]

                # Bound mouse position by edges of screen
                if avgs[0] < 0:
                    avgs[0] = 0
                elif avgs[0] > self.screen_x:
                    avgs[0] = self.screen_x

                if avgs[1] < 0:
                    avgs[1] = 0
                elif avgs[1] > self.screen_y:
                    avgs[1] = self.screen_y

                #Move mouse cursor
                pos_x, pos_y = avgs[0], avgs[1]
                # Uncomment this like to scale the positions when using a webcam.
                #pos_x, pos_y = self.scale_position(avgs[0], avgs[1])

                # Switch the comments on these two lines to give free movement of the mouse.
                self.findClosestCenter((pos_x, pos_y))
                #pyautogui.moveTo(pos_x, pos_y)
