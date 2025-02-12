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
    engine.say("How can I help ?")
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
                        requests.post("http://192.168.0.111:9091/jsonrpc", json = { "jsonrpc": "2.0", "id": 0, "method": "Addons.ExecuteAddon", "params": { "addonid": "script.dialog.scroller", "params": {"image": "http://192.168.0.111:8080/images/about.png", "line": "Vprašanje:"+recognized_text, "time":10}}})
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
    if len(word)>0:
        engine.say("Please wait. I am thinking....")
        API_KEY = "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"
        API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"  # Example endpoint

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek/deepseek-r1-distill-llama-70b:free",
            "messages": [{"role": "user", "content": word+", use up to 200 tokens"}]
        }
        engine.runAndWait()
        response = requests.post(API_ENDPOINT, headers=headers, json=data)
        
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            print(answer)
        else:
            print(f"Error: {response.status_code}", response.text)
            answer = "error. "+response.text
            
        requests.post("http://192.168.0.111:9091/jsonrpc", json = { "jsonrpc": "2.0", "id": 0, "method": "Addons.ExecuteAddon", "params": { "addonid": "script.dialog.scroller", "params": {"image": "http://192.168.0.111:8080/images/about.png", "line": answer, "time": len(answer)}}})
        engine.say(answer)
        engine.runAndWait()