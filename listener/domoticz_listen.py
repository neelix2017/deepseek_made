#Install the required libraries:
#
#pip install vosk sounddevice numpy
#
#Download a Vosk model:https://alphacephei.com/vosk/models
#
#Visit the Vosk models page and download a model (e.g., vosk-model-small-en-us-0.15 for English).
#
#Extract the model and place it in the same directory as the script or provide the path to the model in the script.
import keyboard
import sys
import os
import queue
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer,SetLogLevel
import json
import requests
from datetime import datetime,timedelta
import winsound
import logging

list_of_words = [
                   "tv", "radio","oto", "nick junior", "stop","lights on","lights off","show temperature","show radar","what's the weather like today","blinds","daily news","help","vacuum","music"

                ]
                

# Parameters
SAMPLE_RATE = 16000  # Sample rate for audio recording
CHUNK_SIZE = 4000    # Number of frames per buffer
LISTENING_TIME = 4
EXEC = False
MODEL_PATH = "vosk-model-small-en-us-0.15"  # Path to the Vosk model
logging.basicConfig(filename="Listener.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(name=__name__)


# Check if the model exists
if not os.path.exists(MODEL_PATH):
    print(f"Error: Vosk model not found at {MODEL_PATH}.")
    print("Please download a model from https://alphacephei.com/vosk/models and update the MODEL_PATH.")
    exit(1)


SetLogLevel(-1)
# Load the Vosk model
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE,  "[\""+"\", \"".join(list_of_words)+"\"]" )
# You can also specify the possible word list
#rec = KaldiRecognizer(model, 16000, '["one", "two"]')

# Queue to hold audio data
audio_queue = queue.Queue()

# Callback function to process audio chunks
def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(bytes(indata))

# Start recording from the microphone
def listen():
    global Listening
    #print("Listening... Speak now! (Press Ctrl+C to stop)")
    global list_of_words
    winsound.Beep(4000, 100)
    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=CHUNK_SIZE,
        dtype="int16",
        channels=1,
        callback=audio_callback,
    ):
        try:
            while Listening:
                # Get audio data from the queue
                data = audio_queue.get()
                if (datetime.now()-_start > timedelta(seconds=LISTENING_TIME)):
                    Listening = False
                # Process the audio chunk with Vosk
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    result_dict = json.loads(result)
                    recognized_text = result_dict.get("text", "")
                    if recognized_text:
                        logger.debug(f" Zaznana beseda '{recognized_text}'")
                        return(recognized_text)
                #else:
                #    partial_result = recognizer.PartialResult()
                #    partial_dict = json.loads(partial_result)
                #    partial_text = partial_dict.get("partial", "")
                #    if partial_text:
                #        print("Partial Result:", partial_text)
        except KeyboardInterrupt:
            print("\nStopped listening.")
        winsound.Beep(2000, 55)
        return ""

        
def on_key_press(event):
    #print(event.name)
    global EXEC
    if (not EXEC):
     if (event.event_type == keyboard.KEY_DOWN):
      if (event.name=='browser search key'):
        #print('Speak !')
        EXEC = True
        logger.debug(f" Poslušam ....")
        global Listening
        global _start
        Listening = True
        _start = datetime.now()
        word=listen()
        if len(word)>0:
            print("Zaznana beseda :  "+word,end='\r')
            try:
                m = word.replace(" ", "").replace("'", "")
                if os.path.exists('listener_libs/'+m+".py"):
                    '''if m not in sys.modules:
                        __import__(str('listener_libs.'+m), globals(), locals(), ['start'], 0).start()
                    else:
                        module = sys.modules[str('listener_libs.'+m)]
                        module.start()
                    '''
                    file = open('listener_libs/'+m+".py", "r")
                    content = file.read()                    
                    file.close()
                    exec(content, globals())
                    start()
            except Exception as exc:
                print("Error :"+str(exc))
            finally:
                requests.post("http://192.168.0.111:9091/jsonrpc", json = { "jsonrpc": "2.0", "id": 0, "method": "Addons.ExecuteAddon", "params": { "addonid": "script.dialog.scroller", "params": {"image": "http://192.168.0.111:8080/images/about.png", "line": "Razumel sem : '"+word+"'", "time": "10"}}})
        EXEC = False
        
if __name__ == "__main__":
    logger.debug(f" Besede {str(list_of_words)}")
    for w in list_of_words:
        print(w)
    keyboard.hook(on_key_press, suppress=False)
    print(".....POSLUŠALEC.....")
    print("Press 'BrowserSearch' to speak...")
    print("Press 'ESC' to exit...")
    keyboard.wait('esc')
    keyboard.unhook_all()