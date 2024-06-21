import pathlib
import pyaudio 
import sounddevice as sd
import numpy as np
import pyttsx3
import speech_recognition as sr
import nltk 
import random
import warnings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC

warnings.simplefilter('ignore')
ScriptDir = pathlib.Path().absolute()

# nltk.download("punkt")

def speak(text): 
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print("")
    print(f"==> Parzefal AI : {text}")
    print("")
    Id = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0'
    engine.setProperty('voices',Id)
    engine.say(text=text)
    engine.runAndWait()
    
def speechrecognition():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening.....")
        r.pause_threshold = 1
        audio = r.listen(source,0,8)
        
    try:
        print("Recognizing....")
        query = r.recognize_google(audio,language="en")
        return query.lower()
    
    except:
        return ""


threshold = 20
clap = False

def detect_clap(indata,frames,time,status):
    global clap
    volume_norm = np.linalg.norm(indata)*10
    if volume_norm > threshold:
        clap = True
        print("clap")
    return

def listen_for_claps():
    with sd.InputStream(callback=detect_clap):
        return sd.sleep(1000)
    
def MainClapExe():

    while True:
        listen_for_claps()
        if clap==True:
            break
        
        else:
            pass 
        

url = "https://flowgpt.com/chat"
chrome_option = Options()
user_agent = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"
chrome_option.add_argument(f"user-agent{user_agent}")
chrome_option.add_argument('--profile-directory=Default')
chrome_option.add_argument(f'user-data-dir={ScriptDir}\\chromedata')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_option)
driver.maximize_window()
driver.get(url=url)
# sleep(500)
ChatNumber = 3

def Checker():
    global ChatNumber
    for i in range(1,1000):
        if i % 2 !=0:
            try:
                ChatNumber = str(i)
                Xpath = f"/html/body/div[1]/main/div[3]/div/div[2]/div/div[3]/div[2]/div/div[1]/div/div[{ChatNumber}]/div/div/div/div[1]"
                driver.find_element(by=By.XPATH,value=Xpath)
                
            except:
                print(f"The next chatnumber is: {i} ")
                ChatNumber = str(i)
                break
                
def WebsiteOpener():
    while True:
        try:
            xPath = '/html/body/div[1]/main/div[3]/div/div[2]/div/div[3]/div[2]/div/div[2]/div[2]/div[3]/textarea'
            driver.find_element(by=By.XPATH,value=xPath)
            break
        except:
            pass
        
def SendMessage(Query):
    xPath = '/html/body/div[1]/main/div[3]/div/div[2]/div/div[3]/div[2]/div/div[2]/div[2]/div[3]/textarea'
    driver.find_element(by=By.XPATH,value=xPath).send_keys(Query)
    sleep(1)
    xPath2 ='/html/body/div[1]/main/div[3]/div/div[2]/div/div[3]/div[2]/div/div[2]/div[2]/div[3]/button'
    driver.find_element(by=By.XPATH,value=xPath2).click()
    
def Resultscraper():
    global ChatNumber
    ChatNumber = str(ChatNumber)
    Xpath = f"/html/body/div[1]/main/div[3]/div/div[2]/div/div[3]/div[2]/div/div[1]/div/div[{ChatNumber}]/div/div/div/div[1]"
    Text = driver.find_element(by=By.XPATH,value=Xpath).text
    ChatNumberNew = int(ChatNumber) + 2
    ChatNumber = ChatNumberNew
    return Text

# def Popupremover():
#   Xpath = '/html/body/div[3]/div[3]/div/section/div/div[3]/button[2]'
#   driver.find_element(by=By.XPATH,value=Xpath).click()

# /html/body/div[1]/main/div[3]/div/div[2]/div/div[3]/div[2]/div/div[1]/div/div[5]/div/div/div/div[1]
# /html/body/div[1]/main/div[3]/div/div[2]/div/div[3]/div[2]/div/div[1]/div/div[7]/div/div/div/div[1]
# Popupremover()
# sleep(5000)

def waitfortheanswer():    
    sleep(2)
    XpAth = '/html/body/div[1]/main/div[3]/div/div[2]/div/div[3]/div[2]/div/div[2]/div[1]/div/button'
    while True:
        try:
            driver.find_element(by=By.XPATH,value=XpAth)
        except:
            break
# MainClapExe()
# sleep(2)
WebsiteOpener()
Checker()

while True:
    query = speechrecognition()
    if len(str(query))<3:
        pass
     
    elif query==None:
        pass
        
    else:
        SendMessage(Query=query)
        waitfortheanswer()
        Text = Resultscraper()
        speak(Text)
        
        