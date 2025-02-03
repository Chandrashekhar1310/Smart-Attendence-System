import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
import sys
import time



#start web cam
cap = cv2.VideoCapture(0)
names = []

#function for attendance file

fob = open('attendance.txt','a+')

def enterData(z):
    print("student is", z)
    if z in names:
        pass
    else:
        names.append(z)
        z="".join(str(z))
        fob.write(f"{z} \n")
        return z

print('Reading code.......')



# function for cheacking data is present or not

def checkData(data):
    data=str(data)
    if data in names:
        print('Already present')
    else:
        print ('\n' + str(len(names)+1)+ '\n' +'present done')
        enterData(data)

# command for webcam to read qr
while True:
    _,frame = cap.read()
    decodedObject = pyzbar.decode(frame)
    for obj in decodedObject:
        checkData(obj.data)
        time.sleep(1)

    cv2.imshow('Frame',frame)

    #close
    if cv2.waitKey(1)&0xff==ord('s'):

        cv2.destroyAllWindow()
        break

fob.close()

