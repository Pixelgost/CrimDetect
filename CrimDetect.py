##Install all needed Dependencies
import cv2
from deepface import DeepFace
import glob
import tkinter as tk
import requests 
from bs4 import BeautifulSoup as SOUP
from PIL import Image
import ctypes
##Declare a Static Zip Code Variable
class mymain:
    ZipCode = ''
##Obtain the trained haar cascade for Face Detection
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
##Obtain video capture device and make sure it can be read
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError ("Cannot open Camera!")
##Get List of Files of Approved and Not Approved individuals
ApprovedFiles = glob.glob('Approved/*.jpeg')
NotApprovedFiles = glob.glob('NotApproved/*.jpg')
UnknownFiles = glob.glob('Unknowns/*.jpg')
MugshotFiles = glob.glob('Mugshots/*.jpg')
##Create the ZipCodes that are supported by the Criminal Search Feature
DelCoZips = [74331, 74338, 74342, 74344, 74345, 74346, 74347, 74359, 74364, 74365, 74366, 74368, 74370, 74964]
##Create the UI for Zip Code input, including canvas, buttons, and titles
root= tk.Tk()
#Set the Title of input window
root.title('Input your Zip Code')
#Create the Canvas
Canvas = tk.Canvas(root, width = 400, height = 300)
Canvas.pack()
#Create an Input field in the window
Entry = tk.Entry (root) 
Canvas.create_window(200, 140, window=Entry)
#A Method for fetching the ZipCode when Input is given
def AddZipCode ():  
    X = Entry.get()
    mymain.ZipCode = X
    root.destroy()
#Create a button to submit the zipcode and make it call the AddZipCode() function
Button = tk.Button(text='Submit Zip Code', command=AddZipCode)
Canvas.create_window(200, 180, window=Button)
root.mainloop()
#declare item variable for image scraping later
item = []
#Create a method to display an error messoge
def ShowError(message):
    ctypes.windll.user32.MessageBoxW(0, message, "Error", 1)
#Check if ZipCode is a number and if it is the correct length, if either error is thrown show an error and exit the program. Otherwise transwer the int version of ZipCode for later use
if (len(mymain.ZipCode)!=5):
    ShowError("Incorrect Zip Code!")
    exit()
try:
    mymain.ZipCode = int(mymain.ZipCode)
except ValueError:
    ShowError("Incorrect Zip Code!")
    exit()
#Declare if you can do the Criminal Check
CriminalFeature = False
for ints in DelCoZips:
    if mymain.ZipCode == ints:
        CriminalFeature = True
##If they are in the allowed regions, download/update the local directory with pictures of offenders from the delaware county website, otherwise show an error
imagecount = 0
if(CriminalFeature):
    ##Loop through all 4 pages of the website and download the mugshots
    for h in range(0,4):
        url = 'https://delcosheriff.org/inmate-search.php?pageNum_WADAbooking2='+str(h)+'&totalRows_WADAbooking2=78'
        requestText = requests.get(url).text
        S = SOUP(requestText, 'html.parser')
        ##Get all images on the site
        item = S.find_all('img')
        ##Download the images into a specific directory
        for Items in item:
            with open('Mugshots/'+(str(imagecount))+' crim.jpg', "wb") as f:
                f.write(requests.get(('https://delcosheriff.org/'+Items['src'])).content)
            imagecount +=1
        ## Change the Mugshot Files to the new files
        MugshotFiles = glob.glob('Mugshots/*.jpg') 
else:
    ShowError("Criminal Feature is not enabled in your region")
##make a variable to show how many images there are
maximagecount = imagecount
#Create a Method that will check if the user's face matches with a face from a specified Directory
def CheckFile(Files, frame):
    num =0
    FFile= ''
    for ffile in Files:
        try:
            img2 = cv2.imread(ffile)
            z = DeepFace.verify(frame,img2)
            if(z['verified']):
                num +=1
                FFile = ffile
                break
        except ValueError:
            Filler = 0
    return num, FFile
while True:
    try:
        ##Save a frame of the video output
        #ret,frame = cap.read()
        frame = cv2.imread('rdj.jpg')
        ##Analyze the frame for emotions and save the dominant emotion
        result = DeepFace.analyze(frame,actions = ['emotion'])
        emote= result['dominant_emotion']
        ##Declare DisplayText for later
        DisplayText = ''
        ##Convert image to gray for face detection, then draw a rectangle around all faces seen
        gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray1,1.1,4)
        for(x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y),(x+w, y+h), (0,255,0),2)
        ##Declare more variables for later use
        num = 0
        name = ' '
        ##Check if the Face detected is a face from the approved list, if yes then set DisplayText to show who they are, otherwise check other scenarios
        num, File = CheckFile(ApprovedFiles,frame)
        if (num >0):
            name = str(File)[9:-5]
            DisplayText = 'Verified, Person is: ' + name
        else:
            ##Check if Face is a face from the Not approved list, if yes then set DisplayText to show who they are and show they are disapproved, otherwise check to see if they are one of the criminals from before
            num =0
            DisplayText = 'Not Verified'
            num, File = CheckFile(NotApprovedFiles,frame)
            if (num >0):
                name = str(File)[23:-4]
                DisplayText = 'Verified, Person is: ' + name
            if (num >0):
                DisplayText = 'Disapproved Person: ' + name
            else:
                ## If criminal check is available in your ares compare face to the saved mugshots and see if it is one of the Criminals. If yes, display that, otherwise check if they have visited before
                ## This doesn't use CheckFile Method because this needs try catch
                if(CriminalFeature):
                    num = 0
                    num, File = CheckFile(MugshotFiles, frame)
                    if(num >0):
                        DisplayText = 'THIS PERSON IS A CRIMINAL!'
                    else:
                        ##Check if this person has visited before by seeing if they match up with the pictures of people who ahve visited before stored in UnknownFiles, if they ahven't, store their picture for future use
                        DisplayText = 'Unknown PERSON'
                        num = 0
                        File = ''
                        num, File = CheckFile(UnknownFiles, frame)
                        if (num >0):
                            DisplayText = 'This Unknown Person has visited before'
                        else:
                            cv2.imwrite('Unknowns/'+(str(len(UnknownFiles)))+' Unknown.jpg',frame)
                else:
                    ##Check if this person has visited before by seeing if they match up with the pictures of people who ahve visited before stored in UnknownFiles, if they ahven't, store their picture for future use
                    DisplayText = 'Unknown PERSON'
                    num = 0
                    File= ''
                    num, File = CheckFile(UnknownFiles, frame)
                    if (num >0):
                        DisplayText = 'This Unknown Person has visited before'
                    else:
                        cv2.imwrite('Unknowns/'+(str(len(UnknownFiles)))+' Unknown.jpg',frame)
        ##Add the Emotion Texts and the DisplayText to the earlier image
        font = cv2.FONT_HERSHEY_PLAIN
        cv2.putText(frame, emote, (10,50), font, 3, (255,0,0), 2, cv2.LINE_4)
        cv2.putText(frame, DisplayText, (10,100), font, 1, (0,0,255), 2, cv2.LINE_4)
        cv2.imshow('Original video',frame)
    except ValueError:
        ##If no Faces are detected, this error will be thrown and the video input will be displayed with the words 'no face detected'
        font = cv2.FONT_HERSHEY_PLAIN
        cv2.putText(frame, 'No Face Detected', (10,100), font, 2, (255,0,0), 2, cv2.LINE_4)
        cv2.imshow('Original video',frame)
    ##if q key is pressed, stop the break the loop
    if cv2.waitKey(2)&0xFF == ord('q'):
            break
##Stop the video capture and destroy output windows
cap.release()
cv2.destroyAllWindows()
