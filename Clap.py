import pyaudio
import sounddevice as sd
import numpy as np

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
    
if __name__ == "__main__":
    while True:
        listen_for_claps()
        if clap==True:
            break
        
        else:
            pass 
        