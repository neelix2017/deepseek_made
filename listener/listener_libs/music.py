import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices') 
engine.setProperty('voice', voices[1].id) 

_recognizer = KaldiRecognizer(model, SAMPLE_RATE )
# You can also specify the possible word list
#rec = KaldiRecognizer(model, 16000, '["one", "two"]')

# Start recording from the microphone
def start():
    Listening = True
    engine.say("What do you want to hear?")
    engine.runAndWait()

    LISTENING_TIME = 8
    _start = datetime.now()
    with sd.RawInputStream(
        samplerate=16000,
        blocksize=4000 ,
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
                if _recognizer.AcceptWaveform(data):
                    result = _recognizer.Result()
                    result_dict = json.loads(result)
                    recognized_text = result_dict.get("text", "")
                    if recognized_text:
                        print(recognized_text)
                        requests.post("http://192.168.0.111:9091/jsonrpc", json = { "jsonrpc": "2.0", "id": 0, "method": "Addons.ExecuteAddon", "params": { "addonid": "script.dialog.scroller", "params": {"image": "http://192.168.0.111:8080/images/about.png", "line": "Music:"+recognized_text, "time":10}}})
                        answer(recognized_text)
                #else:
                #    partial_result = recognizer.PartialResult()
                #    partial_dict = json.loads(partial_result)
                #    partial_text = partial_dict.get("partial", "")
                #    if partial_text:
                #        print("Partial Result:", partial_text)
        except KeyboardInterrupt:
            print("\nStopped listening.")
        return ""


def answer(word):
    words = word.split()
    if (words[0].lower()=='artist'):
        artist=word.replace(words[0],'').strip().lower()
        x= requests.post("http://192.168.0.111:9091/jsonrpc", json ={"jsonrpc": "2.0", "method": "AudioLibrary.GetArtists", "params": {  "sort": { "order": "ascending", "method": "artist", "ignorearticle": True } }, "id": 1})
        for i in json.loads(x.text)['result']['artists']:
            if (artist == i['artist'].lower()):
                x=requests.post("http://192.168.0.111:9091/jsonrpc", json ={"jsonrpc": "2.0", "method": "Player.Open", "params": {"item":{"artistid": i['artistid']}},  "id": 1})
    elif (words[0].lower()=='album'):
        album=word.replace(words[0],'').strip().lower()
        x= requests.post("http://192.168.0.111:9091/jsonrpc", json ={"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "params": {  "sort": { "order": "ascending", "ignorearticle": True } }, "id": 1})
        for i in json.loads(x.text)['result']['albums']:
            if (artist == i['label'].lower()):
                x=requests.post("http://192.168.0.111:9091/jsonrpc", json ={"jsonrpc": "2.0", "method": "Player.Open", "params": {"item":{"albumid": i['albumid']}},  "id": 1})

#x=requests.post("http://192.168.0.111:9091/jsonrpc", json ={"jsonrpc": "2.0", "method": "Player.Open", "params": {"item": { "directory": "d:/Music/cache/VA - Repki 2 (2024)"}, "options": {"repeat": "all", "shuffled": False}}, "id": 1})