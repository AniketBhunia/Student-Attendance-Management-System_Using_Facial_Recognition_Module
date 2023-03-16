import cv2
import numpy as np 
import face_recognition
import os
from datetime import datetime 
import mysql.connector
from mysql.connector  import Error

path = 'images'
images = []
classNames = []
existing_name = []
date = []
myList = os.listdir(path)
# print(myList)

for cls in myList:
    curImg = cv2.imread(f'{path}/{cls}')
    images.append(curImg)
    classNames.append(os.path.splitext(cls)[0])
# print(classNames)


def encodeit(iamges):
    encodelist = []
    for img in iamges:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodelist.append(encode)
    # def preencode(file):
    #        file = cv2.cvtColor(file, cv2.COLOR_BGR2RGB)
    #        pre_encode = face_recognition.face_encodings(file)[0]
    #        encodelist.append(pre_encode)
    return encodelist

def extract(name):
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='Students_Details',
                                            user='root',
                                            password='8990mini')
        cursor = connection.cursor()
        sql_select_query = """select Roll_No from details where S_name = %s"""
        cursor.execute(sql_select_query,(name,))
        record = cursor.fetchall()

        for row in record:
           return row[0]
    except mysql.connector.Error as error:
        print("Failed to get record from MySQL table: {}".format(error))

def insert(S_id,S_name,Arriaval_Time,Date):
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='Students_Details',
                                            user='root',
                                            password='8990mini')
        cursor = connection.cursor()
        mySql_insert_query = """INSERT INTO date (S_Id, S_Name, Arriaval_Time,Date) 
                                VALUES (%s, %s, %s,%s) """
        record = (S_id,S_name,Arriaval_Time,Date)
        cursor.execute(mySql_insert_query, record)
        connection.commit()
        print("Record inserted successfully into Student table")
        
    except mysql.connector.Error as error:
        print("Failed to create table in MySQL: {}".format(error))

def markAttdendance(name):
    Roll = extract(name)
    now = datetime.now()
    datetimestring = now.strftime('%H:%M:%S')
    today = datetime.today()
    # todaystring = today.strftime('%Y-%m-%d')
    # date.append(todaystring)
    if name not in existing_name:
        # extract(name)
        insert(Roll,name,datetimestring,today)
        existing_name.append(name)


encodeListKnown = encodeit(images)
print(str(len(encodeListKnown))+" Images Encoding Completed")
#encode = face_recognition.face_encodings(img)[0]

facecam = cv2.VideoCapture(0)
while True:
    ret,frame = facecam.read()
    frameS = cv2.resize(frame,(0,0),None,0.25,0.25)
    frameS = cv2.cvtColor(frameS, cv2.COLOR_BGR2RGB)


    facesCurFrame = face_recognition.face_locations(frameS)
    encodeofCurrFrame = face_recognition.face_encodings(frameS,facesCurFrame)

    for encodeFace,faceLoc in zip(encodeofCurrFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        # print(faceDis)
        matchIndex = np.argmin(faceDis)


        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            # print(name)
            y1,x2,y2,x1 = faceLoc
            y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,255),2)
            cv2.rectangle(frame,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(frame,name,(x1+6,y2-6),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
            markAttdendance(name)
        else:
            y1,x2,y2,x1 = faceLoc
            y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,255),2)
            cv2.rectangle(frame,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(frame,'Unknown',(x1+6,y2-6),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
    cv2.imshow("Facecam",frame)
    key = cv2.waitKey(30)
    if key is ord("f"):
        break
cv2.destroyAllWindows


