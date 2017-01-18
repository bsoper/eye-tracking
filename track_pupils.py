import cv2 

def findEyeCenter(gray_eye, thresh_eye):
    """ findEyeCenter: approximates the center of the pupil by selecting
        the darkest point in gray_eye that is within the blob detected in 
        thresh_eye
        
        args:
            - gray_eye: gray-scale image of eye
            - thresh_eye: binary eye image with contours filled in"""
    
    dims = gray_eye.shape # get shape image
    minBlack = 300
    pupil = [0, 0]
    
    for i in xrange(dims[0]):
        for j in xrange(dims[1]):
            if thresh_eye[i][j]:
                if gray_eye[i][j] < minBlack:
                    minBlack = gray_eye[i][j]
                    pupil[0] = i
                    pupil[1] = j
    
    return pupil
    
#
## main function
#
            
if __name__ == '__main__':    
    face_cascade = cv2.CascadeClassifier('/Users/bsoper/Downloads/opencv-2.4.10/data/haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('/Users/bsoper/Downloads/opencv-2.4.10/data/haarcascades/haarcascade_eye.xml')
    
    if face_cascade.empty():
        print "did not load classifier"
        
    if eye_cascade.empty():
        print "did not load eye classifier"
    
    cap = cv2.VideoCapture('/Users/bsoper/Movies/eye_tracking/face.mov')
    
    while(cap.isOpened()):
        # pull video frame
        ret, img = cap.read()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
        # get faces
        faces = face_cascade.detectMultiScale(img, 1.3, 5)
        
        for (x,y,w,h) in faces:
            # pull face sub-image
            gray_face = gray[y:y+h, x:x+w]
            face = img[y:y+h, x:x+w]
            
            eyes = eye_cascade.detectMultiScale(gray_face) # locate eye regions
            for (ex,ey,ew,eh) in eyes:
                gray_eye = gray_face[ey:ey+eh, ex:ex+ew] # get eye
                eye = face[ey:ey+eh, ex:ex+ew]
                
                # apply gaussian blur to image
                blur = cv2.GaussianBlur(gray_eye, (15,15), 3*gray_eye.shape[0])
                
                retval, thresh = cv2.threshold(~blur, 150, 255, cv2.THRESH_BINARY)
                
                contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                cv2.drawContours(thresh, contours, -1, (255, 255, 255), -1)
                #circles = cv2.HoughCircles(thresh, cv2.cv.CV_HOUGH_GRADIENT, 1, 1) 
                
                pupil = findEyeCenter(gray_eye, thresh)
                
                #cv2.circle(eye, pupil, 0, (0,255,0), -1)
                cv2.circle(img, (pupil[1] + ex + x, pupil[0] + ey + y), 2, (0,255,0), -1)
        
        cv2.imshow('frame', img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite('bad_eye.jpg', img)
            break
        

# cleanup        
cap.release()
cv2.destroyAllWindows()

