# OpenCV program to detect cat face in real time  
# import libraries of python OpenCV  
# where its functionality resides  
import cv2 
from picamera2 import Picamera2
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
from time import sleep     # Import the sleep function from the time module
# load the required trained XML classifiers  
# https://github.com/Itseez/opencv/blob/master/  
# data/haarcascades/haarcascade_frontalcatface.xml  
# Trained XML classifiers describes some features of some  
# object we want to detect a cascade function is trained  
# from a lot of positive(faces) and negative(non-faces)  
# images.  
face_cascade = cv2.CascadeClassifier('haarcascade_frontalcatface.xml')  
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)   # Set pin 8 to be an output pin and set initial value to low (off)
  
# capture frames from a camera  
cap = Picamera2()
cap.start()

# loop runs if capturing has been initialized.  
while 1:  
  
    # reads frames from a camera  
    img = cap.capture_array() 
  
    # convert to gray scale of each frames  
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  
  
    # Detects faces of different sizes in the input image  
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)  
    
    for (x,y,w,h) in faces:  
        # To draw a rectangle in a face  
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,0),2)  
        roi_gray = gray[y:y+h, x:x+w]  
        roi_color = img[y:y+h, x:x+w]  
        print("Gatito Detectado")
        GPIO.output(8, GPIO.HIGH) # Turn on
    if len(faces) == 0:
        GPIO.output(8, GPIO.LOW)
